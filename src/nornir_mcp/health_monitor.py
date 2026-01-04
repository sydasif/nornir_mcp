"""Health monitoring logic and Nornir tasks for network devices.

This module provides comprehensive health monitoring capabilities for network devices
using NAPALM. It includes functions for calculating health scores, determining
health status using emoji indicators, and performing detailed health checks on
device memory usage, CPU temperature, and interface errors.

The health monitoring includes:
- Memory usage analysis (health decreases if usage exceeds 80%)
- CPU temperature monitoring (health decreases if temp exceeds 70°C)
- Interface error detection (health decreases if rx/tx errors > 100)
- Scoring algorithm that calculates an overall 0-100 health score
- Emoji-based health indicators (💚 for excellent, 💛 for good, 🧡 for fair, ❤️ for poor)
"""
from datetime import datetime
from nornir_napalm.plugins.tasks import napalm_get


def _calculate_health_score(checks):
    """Calculate overall health score (0-100)."""
    scores = {
        '✅': 100,
        '⚠️': 70,
        '❌': 30,
        '🔥': 50
    }

    if not checks:
        return 0

    total_score = sum(scores.get(check['status'], 0) for check in checks.values())
    return total_score // len(checks)


def _get_health_emoji(score):
    """Get emoji based on health score."""
    if score >= 90:
        return "💚"
    elif score >= 70:
        return "💛"
    elif score >= 50:
        return "🧡"
    else:
        return "❤️"


def health_check_task(task):
    """Nornir task to gather data and calculate health."""

    # Gather data (Facts, Interfaces, Environment)
    # We use optional_args to pass secret/enable password if defined in inventory
    result = task.run(
        task=napalm_get,
        getters=["facts", "interfaces_counters", "environment"],
        optional_args={"secret": task.host.password}
    )

    # napalm_get returns a MultiResult, the data is in index 0
    data = result[0].result

    facts = data.get("facts", {})
    env = data.get("environment", {})
    interfaces = data.get("interfaces_counters", {})

    health_report = {
        'timestamp': datetime.now().isoformat(),
        'hostname': task.host.name,
        'checks': {}
    }

    # 1. Device Info
    if facts:
        health_report['device_info'] = {
            'model': facts.get('model'),
            'uptime': facts.get('uptime'),
            'vendor': facts.get('vendor')
        }

    # 2. Memory usage
    if env and 'memory' in env:
        memory = env['memory']
        if memory.get('available_ram', 0) > 0:
            used_percent = (memory['used_ram'] / memory['available_ram']) * 100
            health_report['checks']['memory'] = {
                'status': '✅' if used_percent < 80 else '⚠️',
                'used_percent': round(used_percent, 2),
                'message': f"Memory usage: {used_percent:.1f}%"
            }

    # 3. CPU temperature
    if env and 'cpu' in env:
        # Filter out CPUs that might not have temperature readings
        cpu_temps = [v['temperature'] for k, v in env['cpu'].items() if 'temperature' in v]
        if cpu_temps:
            avg_temp = sum(cpu_temps) / len(cpu_temps)
            health_report['checks']['temperature'] = {
                'status': '✅' if avg_temp < 70 else '🔥',
                'avg_celsius': round(avg_temp, 1),
                'message': f"CPU temp: {avg_temp:.1f}°C"
            }

    # 4. Interface errors
    if interfaces:
        error_interfaces = []
        for intf, counters in interfaces.items():
            if counters.get('rx_errors', 0) > 100 or counters.get('tx_errors', 0) > 100:
                error_interfaces.append(intf)

        health_report['checks']['interfaces'] = {
            'status': '✅' if not error_interfaces else '⚠️',
            'error_count': len(error_interfaces),
            'message': f"Interfaces with errors: {len(error_interfaces)}"
        }

    # Calculate Final Score
    if health_report['checks']:
        score = _calculate_health_score(health_report['checks'])
        health_report['health_score'] = score
        health_report['health_emoji'] = _get_health_emoji(score)
    else:
        health_report['status'] = "warning"
        health_report['message'] = "Insufficient data to calculate health."

    return health_report

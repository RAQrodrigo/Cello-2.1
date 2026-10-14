"""
Uses Py4J to invoke a Java program in an already running JVM to interface with the eugene.jar to run the eugene script.
The script runs Eugene's permute function, which generates all valid part orders based on the UCF rules.
These part orders are then used for SBOL and other file generation.

This utilizes the miniEugene-core program.  Please see github or the included md file for copyright information.
https://github.com/CIDARLAB/miniEugene-core

"""

import logging
import re
import time
import itertools

from core_algorithm.utils import log


def call_mini_eugene(rules: list[str], orders_count: int = 100):
    """
    Calls miniEugene to find valid part orders based on the given rules.
    
    :param rules: List of Eugene rules
    :param orders_count: -1 to find ALL valid permutations (may be prohibitively long)
    :return: List of valid part orders (max 5)
    """

    from py4j.java_gateway import JavaGateway, GatewayParameters
    # Suppress (useless) console output
    logging.getLogger("py4j").setLevel(logging.INFO)

    # Start gateway if not already running
    from core_algorithm.utils.py4j_gateway.gateway import start_gateway
    import socket
    
    def is_gateway_running():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            result = s.connect_ex(('127.0.0.1', 25333))
            s.close()
            return result == 0
        except:
            return False
    
    gateway_process = None
    if not is_gateway_running():
        gateway_process = start_gateway()
        # Wait for gateway to be ready
        for _ in range(30):
            if is_gateway_running():
                break
            time.sleep(0.5)
    
    try:
        # Connect to JVM and setup to convert to Java-friendly containers
        gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True))
        miniEugeneInstance = gateway.entry_point

        part_count = 0
        max_val = 0
        for rule in rules:
            if 'CONTAINS ' in rule:
                rules.append(f'{rule.split(" ")[1]} EXACTLY 1')
                part_count += 1
        for rule in rules:
            if ' EQUALS ' in rule:
                index = int(re.search(r'(?<=\[)(.*)(?=\])', rule)[0])
                if index > max_val:
                    max_val = index
        if max_val > part_count:
            part_count = max_val + 2

        rules.reverse()

        # Call the miniPermute function in the Java program, which will in turn invoke miniEugene
        java_part_orders = miniEugeneInstance.miniPermute(rules, part_count, orders_count)
        rules.reverse()

        def convert_to_list_of_lists(part_orders):
            if java_part_orders:
                valid_orders = []  # Convert back to Python-friendly form
                for component in java_part_orders:
                    if component[0] is not None:
                        order = []
                        for part in component:
                            order.append(part)
                        valid_orders.append(order)
                return valid_orders
            else:
                log.cf.error("miniEugene did not return valid part orders...")
                return []

        valid_orders = convert_to_list_of_lists(java_part_orders)
        
        if len(valid_orders) > 5:
            selected_orders = []
            for cnt in range(5):
                selected_orders.append(valid_orders[cnt*len(valid_orders)//5])
            return selected_orders
        else:
            return valid_orders
    finally:
        if gateway_process is not None:
            from core_algorithm.utils.py4j_gateway.gateway import terminate_gateway
            terminate_gateway(gateway_process)

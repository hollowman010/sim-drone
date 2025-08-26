#!/usr/bin/env python3
"""
Cost Optimizer for GCP VM Management.
Manages GPU and CPU VMs for optimal cost efficiency in drone simulation workloads.
"""

import argparse
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

from gpu_vm_manager import GPUVMManager
from cpu_vm_manager import CPUVMManager


class CostOptimizer:
    """Optimizes costs for GPU and CPU VM workloads."""

    def __init__(self, gpu_config: str = "config/gpu_vm.json", cpu_config: str = "config/cpu_vm.json"):
        """Initialize the cost optimizer.

        Args:
            gpu_config: Path to GPU VM configuration
            cpu_config: Path to CPU VM configuration
        """
        self.gpu_manager = GPUVMManager(gpu_config)
        self.cpu_manager = CPUVMManager(cpu_config)
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(__name__)

    def get_cost_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get cost summary for both GPU and CPU VMs."""
        try:
            gpu_cost = self.gpu_manager.estimate_cost(hours)
            cpu_cost = self.cpu_manager.estimate_cost(hours)
            total_cost = gpu_cost + cpu_cost
            
            return {
                "gpu_cost": gpu_cost,
                "cpu_cost": cpu_cost,
                "total_cost": total_cost,
                "hours": hours,
                "gpu_status": self.gpu_manager.get_vm_status(),
                "cpu_status": self.cpu_manager.get_vm_status()
            }
        except Exception as e:
            self.logger.error(f"Failed to get cost summary: {e}")
            return {}

    def optimize_for_airsim_workload(self) -> bool:
        """Optimize VMs for AirSim workload (GPU for simulation, CPU for processing)."""
        try:
            self.logger.info("Optimizing for AirSim workload...")
            
            # Start GPU VM for AirSim
            gpu_status = self.gpu_manager.get_vm_status()
            if gpu_status != "RUNNING":
                self.logger.info("Starting GPU VM for AirSim simulation...")
                if not self.gpu_manager.start_gpu_vm():
                    self.logger.error("Failed to start GPU VM")
                    return False
            
            # Start CPU VM for processing
            cpu_status = self.cpu_manager.get_vm_status()
            if cpu_status != "RUNNING":
                self.logger.info("Starting CPU VM for data processing...")
                if not self.cpu_manager.start_cpu_vm():
                    self.logger.error("Failed to start CPU VM")
                    return False
            
            self.logger.info("AirSim workload optimization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to optimize for AirSim workload: {e}")
            return False

    def optimize_for_processing_workload(self) -> bool:
        """Optimize VMs for processing workload (CPU only)."""
        try:
            self.logger.info("Optimizing for processing workload...")
            
            # Stop GPU VM to save costs
            gpu_status = self.gpu_manager.get_vm_status()
            if gpu_status == "RUNNING":
                self.logger.info("Stopping GPU VM to save costs...")
                self.gpu_manager.stop_gpu_vm()
            
            # Start CPU VM for processing
            cpu_status = self.cpu_manager.get_vm_status()
            if cpu_status != "RUNNING":
                self.logger.info("Starting CPU VM for data processing...")
                if not self.cpu_manager.start_cpu_vm():
                    self.logger.error("Failed to start CPU VM")
                    return False
            
            self.logger.info("Processing workload optimization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to optimize for processing workload: {e}")
            return False

    def shutdown_all_vms(self) -> bool:
        """Shutdown all VMs to save costs."""
        try:
            self.logger.info("Shutting down all VMs to save costs...")
            
            # Stop GPU VM
            gpu_status = self.gpu_manager.get_vm_status()
            if gpu_status == "RUNNING":
                self.gpu_manager.stop_gpu_vm()
            
            # Stop CPU VM
            cpu_status = self.cpu_manager.get_vm_status()
            if cpu_status == "RUNNING":
                self.cpu_manager.stop_cpu_vm()
            
            self.logger.info("All VMs shut down successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to shutdown VMs: {e}")
            return False

    def get_vm_ips(self) -> Dict[str, str]:
        """Get IP addresses for both VMs."""
        try:
            return {
                "gpu_ip": self.gpu_manager.get_vm_ip(),
                "cpu_ip": self.cpu_manager.get_vm_ip()
            }
        except Exception as e:
            self.logger.error(f"Failed to get VM IPs: {e}")
            return {}

    def monitor_costs(self, duration_hours: int = 1) -> None:
        """Monitor costs for a specified duration."""
        try:
            self.logger.info(f"Starting cost monitoring for {duration_hours} hours...")
            
            start_time = datetime.now()
            end_time = start_time + timedelta(hours=duration_hours)
            
            while datetime.now() < end_time:
                cost_summary = self.get_cost_summary(1)  # 1 hour estimate
                
                print(f"\n=== Cost Summary ({datetime.now().strftime('%H:%M:%S')}) ===")
                print(f"GPU VM: ${cost_summary.get('gpu_cost', 0):.2f}/hour")
                print(f"CPU VM: ${cost_summary.get('cpu_cost', 0):.2f}/hour")
                print(f"Total: ${cost_summary.get('total_cost', 0):.2f}/hour")
                print(f"GPU Status: {cost_summary.get('gpu_status', 'Unknown')}")
                print(f"CPU Status: {cost_summary.get('cpu_status', 'Unknown')}")
                
                time.sleep(300)  # Check every 5 minutes
                
        except KeyboardInterrupt:
            self.logger.info("Cost monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Cost monitoring failed: {e}")

    def create_cost_report(self, days: int = 30) -> Dict[str, Any]:
        """Create a cost report for the specified number of days."""
        try:
            hours = days * 24
            cost_summary = self.get_cost_summary(hours)
            
            report = {
                "period_days": days,
                "period_hours": hours,
                "estimated_costs": cost_summary,
                "recommendations": self._generate_recommendations(cost_summary),
                "generated_at": datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to create cost report: {e}")
            return {}

    def _generate_recommendations(self, cost_summary: Dict[str, Any]) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        total_cost = cost_summary.get("total_cost", 0)
        gpu_cost = cost_summary.get("gpu_cost", 0)
        cpu_cost = cost_summary.get("cpu_cost", 0)
        
        if total_cost > 100:  # $100 threshold
            recommendations.append("Consider using spot instances for additional cost savings")
            recommendations.append("Implement auto-shutdown for idle periods")
        
        if gpu_cost > cpu_cost * 2:
            recommendations.append("GPU costs are high - consider optimizing AirSim usage")
            recommendations.append("Use GPU only when running complex simulations")
        
        if cpu_cost > 50:
            recommendations.append("CPU costs are high - consider using smaller instance types")
            recommendations.append("Optimize batch processing to reduce runtime")
        
        if not recommendations:
            recommendations.append("Costs are within reasonable limits")
        
        return recommendations


def main():
    """Main function for cost optimization."""
    parser = argparse.ArgumentParser(description="Optimize costs for GPU and CPU VMs")
    parser.add_argument("action", choices=[
        "cost", "airsim", "processing", "shutdown", "ips", "monitor", "report"
    ])
    parser.add_argument("--gpu-config", default="config/gpu_vm.json", help="GPU VM config path")
    parser.add_argument("--cpu-config", default="config/cpu_vm.json", help="CPU VM config path")
    parser.add_argument("--hours", type=int, default=24, help="Hours for cost estimation")
    parser.add_argument("--days", type=int, default=30, help="Days for cost report")
    parser.add_argument("--monitor-hours", type=int, default=1, help="Hours to monitor costs")
    
    args = parser.parse_args()
    
    optimizer = CostOptimizer(args.gpu_config, args.cpu_config)
    
    if args.action == "cost":
        cost_summary = optimizer.get_cost_summary(args.hours)
        print(f"\n=== Cost Summary ({args.hours} hours) ===")
        print(f"GPU VM: ${cost_summary.get('gpu_cost', 0):.2f}")
        print(f"CPU VM: ${cost_summary.get('cpu_cost', 0):.2f}")
        print(f"Total: ${cost_summary.get('total_cost', 0):.2f}")
        
    elif args.action == "airsim":
        success = optimizer.optimize_for_airsim_workload()
        sys.exit(0 if success else 1)
        
    elif args.action == "processing":
        success = optimizer.optimize_for_processing_workload()
        sys.exit(0 if success else 1)
        
    elif args.action == "shutdown":
        success = optimizer.shutdown_all_vms()
        sys.exit(0 if success else 1)
        
    elif args.action == "ips":
        ips = optimizer.get_vm_ips()
        print(f"GPU VM IP: {ips.get('gpu_ip', 'Not available')}")
        print(f"CPU VM IP: {ips.get('cpu_ip', 'Not available')}")
        
    elif args.action == "monitor":
        optimizer.monitor_costs(args.monitor_hours)
        
    elif args.action == "report":
        report = optimizer.create_cost_report(args.days)
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

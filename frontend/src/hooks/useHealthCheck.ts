import { useState, useEffect } from 'react';
import { HealthStatus } from '../types';

export const useHealthCheck = () => {
  const [healthStatus, setHealthStatus] = useState<HealthStatus>({
    status: 'unknown',
    lastChecked: new Date()
  });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('/api/health');
        const status = response.ok ? 'healthy' : 'unhealthy';
        setHealthStatus({
          status,
          lastChecked: new Date()
        });
      } catch (error) {
        setHealthStatus({
          status: 'unhealthy',
          lastChecked: new Date()
        });
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return healthStatus;
};
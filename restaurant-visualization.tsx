import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { User, ChefHat, Utensils, DollarSign, Brush, UserCog, ClipboardList } from 'lucide-react';

const MENU_ITEMS = {
  "Pizza and soda": 25.99,
  "Burger and fries": 18.99,
  "Pasta and wine": 32.99,
  "Salad and water": 15.99,
  "Steak and wine": 45.99,
  "Fish and chips": 22.99,
  "Chicken curry and rice": 28.99
};

const RestaurantVisualization = () => {
  const [activeConnections, setActiveConnections] = useState([]);
  const [activeCustomers, setActiveCustomers] = useState(new Map());
  const [isSimulationRunning, setIsSimulationRunning] = useState(false);
  const [numCustomers, setNumCustomers] = useState(3);
  const [logs, setLogs] = useState([]);
  const [serverAssignments, setServerAssignments] = useState(new Map());

  const agents = [
    { id: 'customer', icon: User, label: 'Customers', x: 50, y: 50, color: 'text-blue-500' },
    { id: 'order', icon: ClipboardList, label: 'Order Agent', x: 200, y: 50, color: 'text-green-500' },
    { id: 'kitchen', icon: ChefHat, label: 'Kitchen Agent', x: 350, y: 50, color: 'text-orange-500' },
    { id: 'serving', icon: Utensils, label: 'Serving Agent', x: 275, y: 150, color: 'text-purple-500' },
    { id: 'billing', icon: DollarSign, label: 'Billing Agent', x: 125, y: 150, color: 'text-yellow-500' },
    { id: 'cleaning', icon: Brush, label: 'Cleaning Agent', x: 125, y: 250, color: 'text-red-500' },
    { id: 'manager', icon: UserCog, label: 'Manager Agent', x: 275, y: 250, color: 'text-gray-500' }
  ];

  const connections = [
    { from: 'customer', to: 'order', label: 'Place Order' },
    { from: 'order', to: 'kitchen', label: 'Process Order' },
    { from: 'kitchen', to: 'serving', label: 'Serve Meal' },
    { from: 'serving', to: 'billing', label: 'Request Bill' },
    { from: 'billing', to: 'customer', label: 'Process Payment' },
    { from: 'customer', to: 'manager', label: 'Leave Table' },
    { from: 'manager', to: 'cleaning', label: 'Clean Table' }
  ];

  const addLog = (message, emoji = '') => {
    setLogs(prev => [...prev.slice(-9), { 
      timestamp: new Date().toLocaleTimeString(),
      message: emoji ? `${emoji} ${message}` : message
    }]);
  };

  const activateConnection = (fromId, toId, customerId) => {
    const connectionId = `${fromId}-${toId}-${customerId}`;
    setActiveConnections(prev => [...prev, connectionId]);
    setTimeout(() => {
      setActiveConnections(prev => prev.filter(conn => conn !== connectionId));
    }, 1000);
  };

  const getRandomDelay = () => {
    return Math.floor(Math.random() * 3000) + 1000;
  };

  const getRandomMenuItem = () => {
    const items = Object.keys(MENU_ITEMS);
    return items[Math.floor(Math.random() * items.length)];
  };

  const processCustomerJourney = async (customerId) => {
    const order = getRandomMenuItem();
    const serverId = Math.floor(Math.random() * 3) + 1;
    
    setActiveCustomers(prev => {
      const newMap = new Map(prev);
      newMap.set(customerId, { order, status: 'arrived' });
      return newMap;
    });
    
    setServerAssignments(prev => {
      const newMap = new Map(prev);
      newMap.set(customerId, serverId);
      return newMap;
    });

    addLog(`Customer ${customerId} arrived at restaurant`, '🎯');

    // Place order
    await new Promise(resolve => setTimeout(resolve, getRandomDelay()));
    activateConnection('customer', 'order', customerId);
    addLog(`Customer ${customerId} ordered: ${order}`, '👤');

    // Process order
    await new Promise(resolve => setTimeout(resolve, getRandomDelay()));
    activateConnection('order', 'kitchen', customerId);
    addLog(`Order Agent: Processing order for Customer ${customerId}`, '📝');

    // Prepare meal
    await new Promise(resolve => setTimeout(resolve, getRandomDelay() * 2));
    activateConnection('kitchen', 'serving', customerId);
    addLog(`Kitchen: Preparing ${order} for Customer ${customerId}`, '👨‍🍳');

    // Serve meal
    await new Promise(resolve => setTimeout(resolve, getRandomDelay()));
    activateConnection('serving', 'billing', customerId);
    addLog(`Server #${serverId}: Serving Customer ${customerId}`, '🧍‍♂️');

    // Process payment
    await new Promise(resolve => setTimeout(resolve, getRandomDelay()));
    activateConnection('billing', 'customer', customerId);
    const amount = MENU_ITEMS[order];
    const tax = amount * 0.08;
    addLog(`Billing: Customer ${customerId} - $${(amount + tax).toFixed(2)}`, '💰');

    // Leave and clean
    await new Promise(resolve => setTimeout(resolve, getRandomDelay()));
    activateConnection('customer', 'manager', customerId);
    addLog(`Customer ${customerId} leaving table`, '👋');

    await new Promise(resolve => setTimeout(resolve, getRandomDelay()));
    activateConnection('manager', 'cleaning', customerId);
    addLog(`Cleaning table after Customer ${customerId}`, '🧹');

    setActiveCustomers(prev => {
      const newMap = new Map(prev);
      newMap.delete(customerId);
      return newMap;
    });

    setServerAssignments(prev => {
      const newMap = new Map(prev);
      newMap.delete(customerId);
      return newMap;
    });
  };

  const runSimulation = () => {
    setIsSimulationRunning(true);
    setLogs([]);
    setActiveCustomers(new Map());
    setServerAssignments(new Map());
    setActiveConnections([]);

    addLog('Restaurant opened!', '🏪');

    // Start multiple customer journeys with random delays
    Array.from({ length: numCustomers }).forEach((_, index) => {
      setTimeout(() => {
        processCustomerJourney(index + 1);
      }, Math.random() * 3000);
    });

    // Calculate maximum possible duration and end simulation
    const maxDuration = (connections.length * 4000) + (numCustomers * 3000);
    setTimeout(() => {
      setIsSimulationRunning(false);
      addLog('Restaurant simulation completed', '🏁');
    }, maxDuration);
  };

  const NetworkNode = ({ agent }) => {
    const Icon = agent.icon;
    const isActive = Array.from(activeConnections).some(conn => 
      conn.startsWith(agent.id) || conn.split('-')[1] === agent.id
    );

    return (
      <div 
        className="absolute transform -translate-x-1/2 -translate-y-1/2"
        style={{ left: agent.x, top: agent.y }}
      >
        <div className={`p-3 rounded-full bg-white shadow-lg border-2 transition-colors duration-300 ${
          isActive ? 'border-blue-500' : 'border-gray-200'
        }`}>
          <Icon className={`w-6 h-6 ${agent.color}`} />
        </div>
        <div className="text-xs font-medium mt-1 text-center">
          {agent.label}
          {agent.id === 'customer' && activeCustomers.size > 0 && (
            <span className="ml-1 text-blue-500">({activeCustomers.size})</span>
          )}
          {agent.id === 'serving' && serverAssignments.size > 0 && (
            <div className="text-xs text-purple-500">
              {Array.from(serverAssignments.values()).map(serverId => `#${serverId}`).join(', ')}
            </div>
          )}
        </div>
      </div>
    );
  };

  const NetworkConnection = ({ from, to, label }) => {
    const fromAgent = agents.find(a => a.id === from);
    const toAgent = agents.find(a => a.id === to);
    
    const dx = toAgent.x - fromAgent.x;
    const dy = toAgent.y - fromAgent.y;
    const length = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx) * 180 / Math.PI;
    
    const isActive = Array.from(activeConnections).some(conn => 
      conn.startsWith(`${from}-${to}`)
    );

    return (
      <div 
        className={`absolute h-0.5 transition-colors duration-300 ${
          isActive ? 'bg-blue-500' : 'bg-gray-200'
        }`}
        style={{
          left: fromAgent.x,
          top: fromAgent.y,
          width: `${length}px`,
          transform: `rotate(${angle}deg)`,
          transformOrigin: '0 0'
        }}
      >
        <span 
          className="absolute text-xs -translate-y-3 bg-white px-1"
          style={{ left: '50%', transform: `translateX(-50%) rotate(${-angle}deg)` }}
        >
          {label}
        </span>
      </div>
    );
  };

  return (
    <Card className="p-6 w-full max-w-4xl mx-auto">
      <div className="space-y-4">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Restaurant Multi-Agent System</h2>
          <div className="flex items-center gap-4">
            <input
              type="number"
              min="1"
              max="10"
              value={numCustomers}
              onChange={(e) => setNumCustomers(parseInt(e.target.value))}
              className="w-20 p-1 border rounded"
              disabled={isSimulationRunning}
            />
            <button
              onClick={runSimulation}
              disabled={isSimulationRunning}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400"
            >
              {isSimulationRunning ? 'Running...' : 'Start Simulation'}
            </button>
          </div>
        </div>

        <div className="relative h-80 border rounded-lg bg-gray-50 mb-4">
          {connections.map((conn) => (
            <NetworkConnection key={`${conn.from}-${conn.to}`} {...conn} />
          ))}
          {agents.map((agent) => (
            <NetworkNode key={agent.id} agent={agent} />
          ))}
        </div>

        <div className="border rounded-lg p-4 bg-gray-50">
          <h3 className="font-medium mb-2">Activity Log</h3>
          <div className="space-y-1">
            {logs.map((log, i) => (
              <div key={i} className="text-sm">
                <span className="text-gray-500">[{log.timestamp}]</span> {log.message}
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default RestaurantVisualization;

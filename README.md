# Multi-Agent System for Restaurant Operations Management
A comprehensive and dynamic Multi-Agent System (MAS) designed to optimize restaurant operations. This system leverages the SPADE framework for seamless communication between several agents managing various restaurant tasks.

## Overview
The Restaurant Operations Management System is designed to improve efficiency in managing restaurant operations, including customer interactions, order processing, kitchen coordination, serving, billing, cleaning, and oversight by a manager agent. The system ensures dynamic task distribution and smooth communication between agents.

## Features
* Dynamic Coordination: Real-time task allocation among agents.
* Distributed Management: Each agent operates independently, handling specific roles.
* Scalability: Easily extendable for additional agents or functionalities.
* Communication: XMPP-based communication using the Prosody server.
* Visualization: Clear output and interaction flow for easy understanding.

## System Architecture
This system follows a Request-Response Architecture, where agents interact to fulfil requests and execute operations. It also adheres to the FIPA agent standard.

## Key Components:
* Agents: Represent distinct roles in the restaurant (e.g., Customer, Kitchen, Serving, etc.).
* Communication Protocol: XMPP for agent-to-agent communication.
* Environment: A single restaurant simulated for real-time operations.
  
## Agents and Their Roles
* Customer Agent: Places orders and communicates preferences.
* Order Agent: Manages order details and passes them to the kitchen.
* Kitchen Agent: Prepares orders and updates their status.
* Serving Agent: Delivers food to customers.
* Billing Agent: Calculates bills and processes payments.
* Cleaning Agent: Ensures tables are cleaned after use.
* Manager Agent: Oversees the system, resolves conflicts, and ensures smooth operation.
  
## Technologies and Tools Used
Programming Language: Python
Framework: SPADE (Smart Python Agent Development Environment)
Communication Protocol: XMPP (Prosody server)

## Future Scope
* Advanced Negotiation: Implement negotiation strategies for resource allocation.
* Machine Learning Integration: Enable learning-based decision-making for agents.
* Multi-Restaurant Support: Extend the system to manage multiple restaurants.
* Customer Feedback Analysis: Incorporate feedback mechanisms for performance improvement.

## Installation and Usage  
1. Clone this repository:  
   ```bash  
   git clone https://github.com/Surani02/Multi-Agent-System-for-Restaurant-Operations-Management.git
   ```  
2. Navigate to the project directory:  
   ```bash  
   cd Multi-Agent-System-for-Restaurant-Operations-Management
   ```  
3. Install dependencies:  
   ```bash  
   pip install spade
   sudo apt install prosody #For Linux
   ```  
4. Run the application:  
   ```bash  
   python ROMS.py  
   ```  

## Contributing  
Contributions are welcome! Feel free to fork the repository, make changes, and submit a pull request.  

## License  
This project is licensed under the MIT License. 

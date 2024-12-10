import asyncio
import random
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message

# Menu items with prices
MENU_PRICES = {
    "Pizza and soda": 25.99,
    "Burger and fries": 18.99,
    "Pasta and wine": 32.99,
    "Salad and water": 15.99,
    "Steak and wine": 45.99,
    "Fish and chips": 22.99,
    "Chicken curry and rice": 28.99
}

def print_separator(char="-", length=50):
    print(f"\n{char * length}")

def print_header(text):
    print_separator()
    print(f"📍 {text}")
    print_separator()

# Customer Agent
class CustomerAgent(Agent):
    def __init__(self, jid, password, completion_event):
        super().__init__(jid, password)
        self.completion_event = completion_event

    class SendOrderBehaviour(OneShotBehaviour):
        def __init__(self, order_message):
            super().__init__()  
            self.order_message = order_message

        async def run(self):
            customer_num = self.agent.name.replace("customer", "").split("_")[0]
            print(f"\n👤 Customer {customer_num}: Preparing to send an order...")
            await asyncio.sleep(2)
            order_msg = Message(to="order_agent@localhost")
            order_msg.set_metadata("performative", "inform")
            order_msg.set_metadata("customer_num", customer_num)
            order_msg.body = self.order_message
            await self.send(order_msg)
            print(f"👤 Customer {customer_num}: Order sent ✅")

    class HandlePaymentBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and "bill" in msg.body:
                customer_num = self.agent.name.replace("customer", "").split("_")[0]
                print(f"\n👤 Customer {customer_num}: Received bill")
                print(f"----------------------------------------")
                print(f"{msg.body}")
                print(f"----------------------------------------")
                print(f"👤 Customer {customer_num}: Processing payment... 💳")
                await asyncio.sleep(2)
                payment_msg = Message(to="billing_agent@localhost")
                payment_msg.set_metadata("performative", "inform")
                payment_msg.body = "Payment confirmed"
                await self.send(payment_msg)
                print(f"👤 Customer {customer_num}: Payment sent ✅")

                depart_msg = Message(to="manager_agent@localhost")
                depart_msg.set_metadata("performative", "inform")
                depart_msg.body = f"Customer {customer_num} leaving table"
                await self.send(depart_msg)
                print(f"👤 Customer {customer_num}: Leaving restaurant 👋")
                self.agent.completion_event.set()
                self.kill()

    async def send_order(self, order_message):
        self.add_behaviour(self.SendOrderBehaviour(order_message))

    async def setup(self):
        self.add_behaviour(self.HandlePaymentBehaviour())

# Order Agent
class OrderAgent(Agent):
    def __init__(self, jid, password, completion_event):
        super().__init__(jid, password)
        self.completion_event = completion_event

    class ReceiveOrderBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=20)
            if msg:
                customer_num = msg.metadata.get("customer_num", "unknown")
                print(f"\n📝 OrderAgent: Received order from Customer {customer_num}")
                print(f"Order details: {msg.body} ✅")
                forward_msg = Message(to="kitchen_agent@localhost")
                forward_msg.set_metadata("performative", "inform")
                forward_msg.set_metadata("customer_jid", str(msg.sender))
                forward_msg.set_metadata("customer_num", customer_num)
                forward_msg.body = msg.body
                await self.send(forward_msg)
                print(f"📝 OrderAgent: Order forwarded to KitchenAgent ➡️")

    async def setup(self):
        self.add_behaviour(self.ReceiveOrderBehaviour())

# Kitchen Agent
class KitchenAgent(Agent):
    def __init__(self, jid, password, completion_event):
        super().__init__(jid, password)
        self.completion_event = completion_event

    class PrepareMealBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=20)
            if msg:
                print(f"\n👨‍🍳 KitchenAgent: New order received")
                print(f"Order details: {msg.body} ✅")
                print("\n👨‍🍳 KitchenAgent: Preparing meal...")
                print("🔪 Cooking in progress...")
                await asyncio.sleep(5)
                ready_msg = Message(to="serving_agent@localhost")
                ready_msg.set_metadata("performative", "inform")
                ready_msg.set_metadata("customer_jid", msg.metadata.get("customer_jid", ""))
                ready_msg.body = f"Meal ready: {msg.body}"
                await self.send(ready_msg)
                print("👨‍🍳 KitchenAgent: Meal prepared and sent to ServingAgent 🍽️")

    async def setup(self):
        self.add_behaviour(self.PrepareMealBehaviour())

# Serving Agent
class ServingAgent(Agent):
    def __init__(self, jid, password, completion_event):
        super().__init__(jid, password)
        self.completion_event = completion_event
        self.customer_assignments = {}

    class ServeMealBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=20)
            if msg:
                customer_jid = msg.metadata.get("customer_jid", "")
                server_id = hash(str(customer_jid)) % 3 + 1
                self.agent.customer_assignments[customer_jid] = server_id
               
                print(f"\n🧍‍♂️ ServingAgent #{server_id}: Received meal to serve")
                print(f"Order details: {msg.body}")
                await asyncio.sleep(3)
                print(f"🧍‍♂️ ServingAgent #{server_id}: Serving meal to customer... 🍽️")
               
                dining_time = random.randint(5, 15)
                await asyncio.sleep(dining_time)
               
                order_content = msg.body.replace("Meal ready: ", "")
               
                bill_msg = Message(to="billing_agent@localhost")
                bill_msg.set_metadata("performative", "inform")
                bill_msg.set_metadata("customer_jid", customer_jid)
                bill_msg.set_metadata("server_id", str(server_id))
                bill_msg.body = "Customer served. Process payment for: " + order_content
                await self.send(bill_msg)
                print(f"\n🧍‍♂️ ServingAgent #{server_id}: Customer finished dining")
                print(f"Notifying BillingAgent for payment processing 💰")

    async def setup(self):
        self.add_behaviour(self.ServeMealBehaviour())

# Billing Agent
class BillingAgent(Agent):
    def __init__(self, jid, password, completion_event):
        super().__init__(jid, password)
        self.completion_event = completion_event

    class ProcessBillBehaviour(CyclicBehaviour):
        async def run(self):
            message = await self.receive(timeout=20)
            if message:
                if "Process payment for" in message.body:
                    print(f"\n💰 BillingAgent: Processing payment request")
                    print("💰 BillingAgent: Calculating bill amount... 🧮")
                    await asyncio.sleep(2)
                   
                    order_content = message.body.replace("Customer served. Process payment for: ", "")
                    bill_amount = MENU_PRICES.get(order_content, 0.0)
                    tax = bill_amount * 0.08
                    total_amount = bill_amount + tax
                    server_id = message.metadata.get("server_id", "unknown")
                    customer_jid = message.metadata.get("customer_jid", "")
                   
                    if customer_jid:
                        bill_msg = Message(to=customer_jid)
                        bill_msg.set_metadata("performative", "inform")
                        bill_msg.body = (f"bill: {order_content}\n"
                                       f"Subtotal: ${bill_amount:.2f}\n"
                                       f"Tax: ${tax:.2f}\n"
                                       f"Total: ${total_amount:.2f}\n"
                                       f"Server: #{server_id}")
                        await self.send(bill_msg)
                        print(f"💰 BillingAgent: Bill sent to customer ✉️")
                        print_separator()

    async def setup(self):
        self.add_behaviour(self.ProcessBillBehaviour())

# Cleaning Agent
class CleaningAgent(Agent):
    def __init__(self, jid, password, completion_event):
        super().__init__(jid, password)
        self.completion_event = completion_event

    class CleanTableBehaviour(CyclicBehaviour):
        async def run(self):
            message = await self.receive(timeout=20)
            if message and "Clean table" in message.body:
                print(f"\n🧹 CleaningAgent: Starting cleanup process")
                print("🧹 CleaningAgent: Cleaning in progress... 🧼")
                await asyncio.sleep(2)
                print(f"🧹 CleaningAgent: Table cleaned and ready! ✨")
                print_separator()

    async def setup(self):
        self.add_behaviour(self.CleanTableBehaviour())

# Manager Agent
class ManagerAgent(Agent):
    def __init__(self, jid, password, completion_event):
        super().__init__(jid, password)
        self.completion_event = completion_event

    class SuperviseBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=20)
            if msg and "leaving table" in msg.body:
                print(f"\n👔 ManagerAgent: Customer departure noticed")
                print(f"👔 ManagerAgent: Notifying cleaning staff...")
               
                cleaning_msg = Message(to="cleaning_agent@localhost")
                cleaning_msg.set_metadata("performative", "inform")
                cleaning_msg.body = f"Clean table after {msg.body}"
                await self.send(cleaning_msg)
            else:
                await asyncio.sleep(5)

    async def setup(self):
        self.add_behaviour(self.SuperviseBehaviour())

# Main execution
async def main():
    try:
        # Create shared service agents
        order_agent = OrderAgent("order_agent@localhost", "12345", None)
        kitchen_agent = KitchenAgent("kitchen_agent@localhost", "12345", None)
        serving_agent = ServingAgent("serving_agent@localhost", "12345", None)
        billing_agent = BillingAgent("billing_agent@localhost", "12345", None)
        cleaning_agent = CleaningAgent("cleaning_agent@localhost", "12345", None)
        manager_agent = ManagerAgent("manager_agent@localhost", "12345", None)

        # Disable security for all agents
        for agent in [order_agent, kitchen_agent, serving_agent,
                     billing_agent, cleaning_agent, manager_agent]:
            agent.verify_security = False

        # Start all service agents
        await asyncio.gather(
            order_agent.start(),
            kitchen_agent.start(),
            serving_agent.start(),
            billing_agent.start(),
            cleaning_agent.start(),
            manager_agent.start(),
        )

        menu_items = list(MENU_PRICES.keys())

        async def random_customer_generator(num_customers):
            customer_tasks = []
            for i in range(1, num_customers + 1):
                delay = random.uniform(1, 10)
                await asyncio.sleep(delay)
                order = random.choice(menu_items)
                task = asyncio.create_task(handle_customer(order, i))
                customer_tasks.append(task)
           
            await asyncio.gather(*customer_tasks)

        async def handle_customer(order, customer_num):
            completion_event = asyncio.Event()
            customer_jid = f"customer{customer_num}_agent@localhost"
            customer_agent = CustomerAgent(customer_jid, "12345", completion_event)
            customer_agent.verify_security = False
           
            await customer_agent.start()
            print_header(f"Customer {customer_num} arrived at the restaurant")
            await customer_agent.send_order(order)

            try:
                await asyncio.wait_for(completion_event.wait(), timeout=120)
                await asyncio.sleep(5)
                print(f"\n✅ Customer {customer_num}'s dining experience completed")
                print_separator()
            except asyncio.TimeoutError:
                print(f"\n⚠️ Timeout waiting for customer {customer_num}'s workflow")
                print_separator()
           
            await customer_agent.stop()

        num_customers = random.randint(3, 8)
        print_header("Restaurant opened!")
        print_separator()
       
        await random_customer_generator(num_customers)
        await asyncio.sleep(5)

        # Stop all service agents
        await asyncio.gather(
            order_agent.stop(),
            kitchen_agent.stop(),
            serving_agent.stop(),
            billing_agent.stop(),
            cleaning_agent.stop(),
            manager_agent.stop(),
        )

        print_header("Restaurant simulation completed")

    except KeyboardInterrupt:
        print_header("Shutdown signal received. Stopping agents...")

if __name__ == "__main__":
    asyncio.run(main())
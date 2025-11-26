from database import buy_lottery_ticket, get_lottery_state, payout_winner

LOTTERY_DATA = {
    "name": "lottery",
    "description": "Global Server Lottery",
    "type": 1,
    "options": [
        {
            "name": "action",
            "description": "Buy a ticket or check status",
            "type": 3,
            "required": True,
            "choices": [
                {"name": "Buy Ticket ($100)", "value": "buy"},
                {"name": "Check Pot", "value": "status"}
            ]
        }
    ]
}

def cmd_lottery(data):
    user_id = data["member"]["user"]["id"]
    action = data["options"][0]["value"]
    
    if action == "status":
        state = get_lottery_state()
        pot = state.get("pot", 0)
        tickets = len(state.get("tickets", []))
        needed = 10 - tickets
        
        return {
            "type": 4,
            "data": {
                "embeds": [{
                    "title": "🎟️ Global Lottery",
                    "description": f"💰 **Current Pot:** ${pot:,}\n🎫 **Tickets Sold:** {tickets}/10\n\n*Lottery draws automatically at 10 tickets!*",
                    "color": 0xf1c40f
                }]
            }
        }

    if action == "buy":
        success, msg = buy_lottery_ticket(user_id, 100)
        
        if not success:
            return {"type": 4, "data": {"content": f"❌ Error: {msg}"}}
            
        if msg.startswith("WINNER"):
            _, winner_id, amount = msg.split("|")
            amount = int(amount)
            
            # Jeśli wygrał ktoś inny niż kupujący, musimy mu teraz dodać kasę (bo transakcja obsługuje tylko 1 usera)
            if winner_id != user_id:
                payout_winner(winner_id, amount)
            
            return {
                "type": 4,
                "data": {
                    "content": f"🎉 **LOTTERY DRAW!** 🎉\nTicket limit reached!",
                    "embeds": [{
                        "title": "🏆 WINNER!",
                        "description": f"<@{winner_id}> just won the **${amount:,}** pot!\n\n*A new lottery has started.*",
                        "color": 0x2ecc71
                    }]
                }
            }
        else:
            return {
                "type": 4,
                "data": {"content": "🎟️ **Ticket purchased!** Good luck."}
            }
"""Buy and Sell Contract Generator"""
from typing import Dict, List
from datetime import datetime

class ContractGenerator:
    def generate(
        self,
        details: Dict,
        special_clauses: List[str],
        applicable_laws: List[Dict]
    ) -> str:
        seller = details.get('seller_name', '[SELLER]')
        buyer = details.get('buyer_name', '[BUYER]')
        item = details.get('item_description', '[ITEM DESCRIPTION]')
        price = details.get('purchase_price', '[PRICE]')
        
        payment_terms = details.get('payment_terms', 'Full payment upon delivery')
        delivery_date = details.get('delivery_date', '[DELIVERY DATE]')
        delivery_place = details.get('delivery_place', '[DELIVERY PLACE]')
        delivery_method = details.get('delivery_method', 'Personal handover / Courier')
        delivery_cost = details.get('delivery_cost', 'Shouldered by Buyer')
        
        return f"""CONTRACT OF SALE

This Contract of Sale is entered into on {datetime.now().strftime('%B %d, %Y')}.

BETWEEN:

SELLER: {seller}  
BUYER: {buyer}

ARTICLE 1 – SUBJECT MATTER

The Seller agrees to sell and the Buyer agrees to purchase the following item:

{item}

ARTICLE 2 – PURCHASE PRICE

2.1 The total purchase price shall be PHP {price}.

ARTICLE 3 – PAYMENT TERMS

3.1 Payment Terms: {payment_terms}

ARTICLE 4 – DELIVERY TERMS

4.1 Delivery Date  
The item shall be delivered on or before {delivery_date}.

4.2 Place of Delivery  
Delivery shall be made at {delivery_place} unless otherwise agreed in writing by both parties.

4.3 Mode of Delivery  
The item shall be delivered through the following method: {delivery_method}.

4.4 Delivery Costs  
All delivery, transportation, and related expenses shall be {delivery_cost}, unless otherwise agreed by the parties.

4.5 Transfer of Ownership and Risk  
Ownership and risk of loss shall transfer from the Seller to the Buyer upon actual delivery of the item.

ARTICLE 5 – WARRANTY

The Seller warrants that:

5.1 The Seller is the lawful owner of the item and has full authority to sell it.  
5.2 The item is free from all liens, encumbrances, and claims of third parties.  
5.3 {details.get('warranty', 'The item is in good and serviceable condition at the time of sale.')}

ARTICLE 6 – RISK OF LOSS

Unless otherwise provided, the risk of loss shall pass to the Buyer upon delivery of the item.

{chr(10).join([f'ADDITIONAL TERM: {clause}' for clause in special_clauses]) if special_clauses else ''}

APPLICABLE PHILIPPINE CIVIL CODE PROVISIONS:

{chr(10).join([f"• Article {law.get('article')}: {law.get('rule', '')[:80]}..." for law in applicable_laws[:3]])}

IN WITNESS WHEREOF, the parties have hereunto affixed their signatures on the date first written above.


_________________          _________________  
{seller}                   {buyer}  
SELLER                     BUYER
"""

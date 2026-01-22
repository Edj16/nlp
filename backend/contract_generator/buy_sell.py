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

The Seller agrees to sell and the Buyer agrees to purchase the following item: {item}. The item is determinate and lawful, in accordance with Article 1458 of the Civil Code of the Philippines.

ARTICLE 2 – PURCHASE PRICE

2.1 The total purchase price shall be PHP {price}, payable in accordance with Article 1582 of the Civil Code, which requires payment at the time and place stipulated or, if not stipulated, at the time and place of delivery.

ARTICLE 3 – PAYMENT TERMS

3.1 Payment Terms: {payment_terms}. For installment sales, the Buyer shall pay in accordance with Article 1484 of the Civil Code, and failure to pay two or more installments may result in rescission or foreclosure.

ARTICLE 4 – DELIVERY TERMS

4.1 Delivery Date: The item shall be delivered on or before {delivery_date}, in accordance with Article 1497 of the Civil Code.

4.2 Place of Delivery: Delivery shall be made at {delivery_place} unless otherwise agreed in writing by both parties.

4.3 Mode of Delivery: The item shall be delivered through the following method: {delivery_method}.

4.4 Delivery Costs: All delivery, transportation, and related expenses shall be {delivery_cost}, unless otherwise agreed by the parties.

4.5 Transfer of Ownership and Risk: Ownership and risk of loss shall transfer from the Seller to the Buyer upon actual or constructive delivery, in accordance with Article 1477 of the Civil Code. For fungible goods sold by weight, number, or measure, risk passes upon delivery per Article 1480.

ARTICLE 5 – WARRANTIES

The Seller warrants that:

5.1 The Seller is the lawful owner of the item and has the right to sell it, pursuant to Article 1547 of the Civil Code.

5.2 The item is free from all liens, encumbrances, and claims of third parties, as required under Article 1547 of the Civil Code.

5.3 The Buyer shall enjoy peaceful and legal possession, in accordance with the warranty against eviction under Article 1548 of the Civil Code.

5.4 The item is free from hidden defects rendering it unfit for its intended use or diminishing its value, subject to the warranty against hidden defects under Article 1561 of the Civil Code.

5.5 If this is a consumer transaction under Republic Act No. 7394 (Consumer Act), the Seller provides implied warranties of merchantability (Article 67) and fitness for purpose (Article 67), unless waived in writing.

ARTICLE 6 – RISK OF LOSS

Unless otherwise provided, the risk of loss shall pass to the Buyer upon delivery of the item, in accordance with Article 1504 of the Civil Code.

ARTICLE 7 – REMEDIES FOR BREACH

7.1 Buyer Remedies: In case of breach of warranty, the Buyer may accept and demand rescission or reduction in price (Article 1599 of the Civil Code). For consumer transactions, remedies include repair, replacement, refund, or price reduction (RA 7394, Article 97).

7.2 Seller Remedies: For non-payment, the Seller may rescind the sale after judicial or notarial demand (Article 1592 for immovable property) or automatically upon expiration of the period if the Buyer does not appear or pay (Article 1593 for movable property). For installment sales, the Seller may exact fulfillment, cancel the sale, or foreclose (Article 1484).

{chr(10).join([f'ADDITIONAL TERM: {clause}' for clause in special_clauses]) if special_clauses else ''}

APPLICABLE PHILIPPINE LAWS:

{chr(10).join([f"• Article {law.get('article')}: {law.get('rule', '')[:80]}..." for law in applicable_laws[:3]])}

IN WITNESS WHEREOF, the parties have hereunto affixed their signatures on the date first written above.

_________________          _________________  
{seller}                   {buyer}  
SELLER                     BUYER

Disclaimer: This template is for informational purposes only and does not constitute legal advice. It is recommended to consult a qualified attorney to ensure compliance with applicable laws and to tailor the contract to your specific circumstances.
"""
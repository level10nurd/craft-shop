# to test lightspeed api via lightspeed developer portal

## test request
### bearer
lsxs_pt_ulgiqwIayaQCsEvqblwwFlgYyaXq6rVS

### url
https://craftcontemporaryshop.retail.lightspeed.app/api/2.0/sales

### request
import requests

url = "https://craftcontemporaryshop.retail.lightspeed.app/api/2.0/sales"

headers = {
    "accept": "application/json",
    "authorization": "Bearer lsxs_pt_ulgiqwIayaQCsEvqblwwFlgYyaXq6rVS"
}

response = requests.get(url, headers=headers)

print(response.text)

### response
{
  "data": [
    {
      "id": "ed290b30-16d8-8911-11ee-0edea74af4f9",
      "outlet_id": "06f2e29c-25cb-11ee-efde-0bc57871a8a0",
      "register_id": "06f2e29c-25cb-11ee-efde-0bc57873d83f",
      "user_id": "06f2e29c-25cb-11ee-efde-0bc5786da0ef",
      "customer_id": "06f2e29c-25cb-11ee-efde-0bc5783ed389",
      "invoice_number": "5",
      "source": "USER",
      "source_id": null,
      "complete_open_sequence_id": null,
      "accounts_transaction_id": null,
      "has_unsynced_on_account_payments": null,
      "status": "CLOSED",
      "note": "",
      "short_code": "0LtVmP",
      "return_for": null,
      "return_ids": [],
      "total_loyalty": 0,
      "created_at": "2023-06-19T20:24:44+00:00",
      "updated_at": "2023-06-19T20:24:44+00:00",
      "sale_date": "2023-06-19T20:24:33+00:00",
      "deleted_at": "2023-07-21T22:20:40+00:00",
      "line_items": [
        {
          "id": "ed290b30-16d8-8725-11ee-0edf11015002",
          "product_id": "d32aa508-970c-46aa-900b-18b8828706db",
          "salesperson_id": null,
          "tax_id": "06f2e29c-25cb-11ee-efde-0bc5786b1950",
          "discount_total": 0,
          "discount": 0,
          "price_total": 40,
          "price": 40,
          "cost_total": 20,
          "cost": 20,
          "tax_total": 0,
          "tax": 0,
          "quantity": 1,
          "loyalty_value": 0,
          "note": null,
          "return_reason": null,
          "price_set": false,
          "status": "CONFIRMED",
          "sequence": 0,
          "gift_card_number": null,
          "tax_components": [
            {
              "rate_id": "786b7567-0bc5-11ee-afde-06f2e29c25cb",
              "total_tax": 0
            }
          ],
          "promotions": [],
          "surcharges": [],
          "total_tax": 0,
          "unit_cost": 20,
          "unit_discount": 0,
          "unit_price": 40,
          "unit_tax": 0,
          "unit_loyalty_value": 0,
          "total_cost": 20,
          "total_discount": 0,
          "total_loyalty_value": 0,
          "total_price": 40,
          "is_return": false
        },
        {
          "id": "ed290b30-16d8-be98-11ee-0edf45e47b97",
          "product_id": "4f37091b-a6bc-48e0-afa0-72f846a8de9d",
          "salesperson_id": null,
          "tax_id": "06f2e29c-25cb-11ee-efde-0bc5786b1950",
          "discount_total": 0,
          "discount": 0,
          "price_total": 160,
          "price": 160,
          "cost_total": 80,
          "cost": 80,
          "tax_total": 0,
          "tax": 0,
          "quantity": 1,
          "loyalty_value": 0,
          "note": null,
          "return_reason": null,
          "price_set": false,
          "status": "CONFIRMED",
          "sequence": 1,
          "gift_card_number": null,
          "tax_components": [
            {
              "rate_id": "786b7567-0bc5-11ee-afde-06f2e29c25cb",
              "total_tax": 0
            }
          ],
          "promotions": [],
          "surcharges": [],
          "total_tax": 0,
          "unit_cost": 80,
          "unit_discount": 0,
          "unit_price": 160,
          "unit_tax": 0,
          "unit_loyalty_value": 0,
          "total_cost": 80,
          "total_discount": 0,
          "total_loyalty_value": 0,
          "total_price": 160,
          "is_return": false
        }
      ],
      "payments": [],
      "adjustments": [],
      "external_applications": [],
      "attributes": [],
      "version": 30648428156,
      "ecom_custom_charges": {
        "charges": [],
        "total": 0,
        "total_tax": 0,
        "total_incl": 0
      },
      "total_tax": 0,
      "receipt_number": "5",
      "total_price_incl": 200,
      "total_surcharge": 0,
      "taxes": [
        {
          "amount": 0,
          "id": "786b7567-0bc5-11ee-afde-06f2e29c25cb"
        }
      ],
      "total_price": 200
    },
    {
      "id": "ed290b30-16d8-8eba-11ee-0ee4340b1c26",
      "outlet_id": "06f2e29c-25cb-11ee-efde-0bc57871a8a0",
      "register_id": "06f2e29c-25cb-11ee-efde-0bc57873d83f",
      "user_id": "06f2e29c-25cb-11ee-efde-0bc5786da0ef",
      "customer_id": "06f2e29c-2544-11ee-efde-0ee40e148f72",
      "invoice_number": "7",
      "source": "USER",
      "source_id": null,
      "complete_open_sequence_id": null,
      "accounts_transaction_id": null,
      "has_unsynced_on_account_payments": null,
      "status": "CLOSED",
      "note": "",
      "short_code": "ZB5iqe",
      "return_for": null,
      "return_ids": [],
      "total_loyalty": 0,
      "created_at": "2023-06-19T21:00:29+00:00",
      "updated_at": "2023-06-19T21:00:29+00:00",
      "sale_date": "2023-06-19T21:00:10+00:00",
      "deleted_at": "2023-07-21T22:20:40+00:00",
      "line_items": [
        {
          "id": "ed290b30-16d8-8eba-11ee-0ee4371d3e27",
          "product_id": "06f2e29c-2544-11ee-efde-0bc579766159",
          "salesperson_id": null,
          "tax_id": "06f2e29c-25cb-11ee-efde-0bc5786b1950",
          "discount_total": 0,
          "discount": 0,
          "price_total": -59,
          "price": 59,
          "cost_total": -30,
          "cost": 30,
          "tax_total": 0,
          "tax": 0,
          "quantity": -1,
          "loyalty_value": 0,
          "note": null,
          "return_reason": null,
          "price_set": false,
          "status": "CONFIRMED",
          "sequence": 0,
          "gift_card_number": null,
          "tax_components": [
            {
              "rate_id": "786b7567-0bc5-11ee-afde-06f2e29c25cb",
              "total_tax": 0
            }
          ],
          "promotions": [],
          "surcharges": [],
          "total_tax": 0,
          "unit_cost": 30,
          "unit_discount": 0,
          "unit_price": 59,
          "unit_tax": 0,
          "unit_loyalty_value": 0,
          "total_cost": -30,
          "total_discount": 0,
          "total_loyalty_value": 0,
          "total_price": -59,
          "is_return": false
        }
      ],
      "payments": [],
      "adjustments": [],
      "external_applications": [],
      "attributes": [],
      "version": 30648428157,
      "ecom_custom_charges": {
        "charges": [],
        "total": 0,
        "total_tax": 0,
        "total_incl": 0
      },
      "total_tax": 0,
      "receipt_number": "7",
      "total_price_incl": -59,
      "total_surcharge": 0,
      "taxes": [
        {
          "amount": 0,
          "id": "786b7567-0bc5-11ee-afde-06f2e29c25cb"
        }
      ],
      "total_price": -59
    },
    {
      "id": "ed290b30-16d8-8eba-11ee-0ee44f6b9fdd",
      "outlet_id": "06f2e29c-25cb-11ee-efde-0bc57871a8a0",
      "register_id": "06f2e29c-25cb-11ee-efde-0bc57873d83f",
      "user_id": "06f2e29c-25cb-11ee-efde-0bc5786da0ef",
      "customer_id": "06f2e29c-2544-11ee-efde-0ee40e148f72",
      "invoice_number": "8",
      "source": "USER",
      "source_id": null,
      "complete_open_sequence_id": null,
      "accounts_transaction_id": null,
      "has_unsynced_on_account_payments": null,
      "status": "LAYBY",
      "note": "",
      "short_code": "W3Edtt",
      "return_for": null,
      "return_ids": [],
      "total_loyalty": 0,
      "created_at": "2023-06-19T21:02:25+00:00",
      "updated_at": "2023-06-19T21:02:25+00:00",
      "sale_date": "2023-06-19T21:01:43+00:00",
      "deleted_at": "2023-07-21T22:20:40+00:00",
      "line_items": [
        {
          "id": "ed290b30-16d8-8eba-11ee-0ee45390434e",
          "product_id": "06f2e29c-2544-11ee-efde-0bc578e98d5e",
          "salesperson_id": null,
          "tax_id": "06f2e29c-25cb-11ee-efde-0bc5786b1950",
          "discount_total": 0,
          "discount": 0,
          "price_total": 25.9,
          "price": 25.9,
          "cost_total": 18,
          "cost": 18,
          "tax_total": 0,
          "tax": 0,
          "quantity": 1,
          "loyalty_value": 0,
          "note": null,
          "return_reason": null,
          "price_set": false,
          "status": "CONFIRMED",
          "sequence": 0,
          "gift_card_number": null,
          "tax_components": [
            {
              "rate_id": "786b7567-0bc5-11ee-afde-06f2e29c25cb",
              "total_tax": 0
            }
          ],
          "promotions": [],
          "surcharges": [],
          "total_tax": 0,
          "unit_cost": 18,
          "unit_discount": 0,
          "unit_price": 25.9,
          "unit_tax": 0,
          "unit_loyalty_value": 0,
          "total_cost": 18,
          "total_discount": 0,
          "total_loyalty_value": 0,
          "total_price": 25.9,
          "is_return": false
        },
        {
          "id": "ed290b30-16d8-8eba-11ee-0ee4742a35d3",
          "product_id": "09ea4561-4b96-4ad6-80ba-2a64761da971",
          "salesperson_id": null,
          "tax_id": "06f2e29c-25cb-11ee-efde-0bc5786b1950",
          "discount_total": 12,
          "discount": 12,
          "price_total": 108,
          "price": 108,
          "cost_total": 60,
          "cost": 60,
          "tax_total": 0,
          "tax": 0,
          "quantity": 1,
          "loyalty_value": 0,
          "note": null,
          "return_reason": null,
          "price_set": false,
          "status": "CONFIRMED",
          "sequence": 1,
          "gift_card_number": null,
          "tax_components": [
            {
              "rate_id": "786b7567-0bc5-11ee-afde-06f2e29c25cb",
              "total_tax": 0
            }
          ],
          "promotions": [],
          "surcharges": [],
          "total_tax": 0,
          "unit_cost": 60,
          "unit_discount": 12,
          "unit_price": 108,
          "unit_tax": 0,
          "unit_loyalty_value": 0,
          "total_cost": 60,
          "total_discount": 12,
          "total_loyalty_value": 0,
          "total_price": 108,
          "is_return": false
        }
      ],
      "payments": [],
      "adjustments": [],
      "external_applications": [],
      "attributes": [
        "layby"
      ],
      "version": 30648428158,
      "ecom_custom_charges": {
        "charges": [],
        "total": 0,
        "total_tax": 0,
        "total_incl": 0
      },
      "total_tax": 0,
      "receipt_number": "8",
      "total_price_incl": 133.9,
      "total_surcharge": 0,
      "taxes": [
        {
          "amount": 0,
          "id": "786b7567-0bc5-11ee-afde-06f2e29c25cb"
        }
      ],
      "total_price": 133.9
    },
    {
      "id": "ed290b30-16d8-9e02-11ee-0ed0577a48bc",
      "outlet_id": "06f2e29c-25cb-11ee-efde-0bc57871a8a0",
      "register_id": "06f2e29c-25cb-11ee-efde-0bc57873d83f",
      "user_id": "06f2e29c-25cb-11ee-efde-0bc5786da0ef",
      "customer_id": "06f2e29c-25cb-11ee-efde-0bc5783ed389",
      "invoice_number": "1",
      "source": "USER",
      "source_id": null,
      "complete_open_sequence_id": null,
      "accounts_transaction_id": null,
      "has_unsynced_on_account_payments": null,
      "status": "SAVED",
      "note": "hana",
      "short_code": "bfdmlb",
      "return_for": null,
      "return_ids": [],
      "total_loyalty": 0,
      "created_at": "2023-06-19T18:39:38+00:00",
      "updated_at": "2023-06-19T18:39:38+00:00",
      "sale_date": "2023-06-19T18:39:32+00:00",
      "deleted_at": "2023-07-21T22:20:40+00:00",
      "line_items": [
        {
          "id": "ed290b30-16d8-9e02-11ee-0ed05a65f6fd",
          "product_id": "06f2e29c-2544-11ee-efde-0bc579766159",
          "salesperson_id": null,
          "tax_id": "06f2e29c-25cb-11ee-efde-0bc5786b1950",
          "discount_total": 0,
          "discount": 0,
          "price_total": 59,
          "price": 59,
          "cost_total": 30,
          "cost": 30,
          "tax_total": 0,
          "tax": 0,
          "quantity": 1,
          "loyalty_value": 0,
          "note": null,
          "return_reason": null,
          "price_set": false,
          "status": "SAVED",
          "sequence": 0,
          "gift_card_number": null,
          "tax_components": [
            {
              "rate_id": "786b7567-0bc5-11ee-afde-06f2e29c25cb",
              "total_tax": 0
            }
          ],
          "promotions": [],
          "surcharges": [],
          "total_tax": 0,
          "unit_cost": 30,
          "unit_discount": 0,
          "unit_price": 59,
          "unit_tax": 0,
          "unit_loyalty_value": 0,
          "total_cost": 30,
          "total_discount": 0,
          "total_loyalty_value": 0,
          "total_price": 59,
          "is_return": false
        },
        {
          "id": "ed290b30-16d8-9e02-11ee-0ed05cbb7fbf",
          "product_id": "06f2e29c-2544-11ee-efde-0bc579f6910c",
          "salesperson_id": null,
          "tax_id": "06f2e29c-25cb-11ee-efde-0bc5786b1950",
          "discount_total": 0,
          "discount": 0,
          "price_total": 35.9,
          "price": 35.9,
          "cost_total": 20,
          "cost": 20,
          "tax_total": 0,
          "tax": 0,
          "quantity": 1,
          "loyalty_value": 0,
          "note": null,
          "return_reason": null,
          "price_set": false,
          "status": "SAVED",
          "sequence": 1,
          "gift_card_number": null,
          "tax_components": [
            {
              "rate_id": "786b7567-0bc5-11ee-afde-06f2e29c25cb",
              "total_tax": 0
            }
          ],
          "promotions": [],
          "surcharges": [],
          "total_tax": 0,
          "unit_cost": 20,
          "unit_discount": 0,
          "unit_price": 35.9,
          "unit_tax": 0,
          "unit_loyalty_value": 0,
          "total_cost": 20,
          "total_discount": 0,
          "total_loyalty_value": 0,
          "total_price": 35.9,
          "is_return": false
        }
      ],
      "payments": [],
      "adjustments": [],
      "external_applications": [],
      "attributes": [],
      "version": 30648428159,
      "ecom_custom_charges": {
        "charges": [],
        "total": 0,
        "total_tax": 0,
        "total_incl": 0
      },
      "total_tax": 0,
      "receipt_number": "1",
      "total_price_incl": 94.9,
      "total_surcharge": 0,
      "taxes": [
        {
          "amount": 0,
          "id": "786b7567-0bc5-11ee-afde-06f2e29c25cb"
        }
      ],
      "total_price": 94.9
try 
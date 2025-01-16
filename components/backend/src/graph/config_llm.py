from datetime import datetime


class ConfigLLM:
    ORDER_SCHEMA = """
    {{
        "_id": "ObjectId",
        "purchaseOrderNumber": "string",
        "creationDate": "Date",
        "purchaseDate": "Date",
        "fiscalYear": "string",
        "departmentName": "string",
        "supplierName": "string",
        "supplierCode": "string",
        "supplierQualifications": "string",
        "acquisitionType": "string",
        "acquisitionMethod": "string",
        "calCardUsed": "string",
        "lineItems": [
            {{
                "itemName": "string",
                "itemDescription": "string",
                "itemDescriptionUUID": "string",
                "quantity": "Double",
                "unitPrice": "Double",
                "totalPrice": "Double",
                "normalizedUNSPSC": "string",
                "commodityTitle": "string",
                "commodityTitleUUID": "string"
            }}
        ]
    }}
    """
    ORDER_SCHEMA_DESCRIPTION = """
    This schema describes the structure and purpose of the fields in a unified collection containing purchase order details and their associated line items. Line items are stored as a nested array within the purchase order document to maintain a hierarchical relationship.

    Purchase Order Fields:
    1. Field Name: _id
      Field Description: Unique identifier for the document in the collection.

    2. Field Name: creationDate
      Field Description: System-generated date indicating when the purchase order was created.

    3. Field Name: purchaseDate
      Field Description: User-provided date of the purchase. It can be earlier than creationDate; therefore, creationDate serves as the primary reference.

    4. Field Name: fiscalYear
      Field Description: Fiscal year derived from the creationDate. For example, in the State of California, the fiscal year starts on July 1 and ends on June 30.

    5. Field Name: purchaseOrderNumber
      Field Description: Identifier for the purchase order, unique within a department but not globally across all departments.

    6. Field Name: departmentName
      Field Description: Normalized name of the department making the purchase.

    7. Field Name: supplierName
      Field Description: Name of the supplier, as registered during account setup.

    8. Field Name: supplierCode
      Field Description: Numeric code uniquely identifying the supplier.

    9. Field Name: supplierQualifications
      Field Description: Certifications or qualifications of the supplier, such as SB (Small Business), DVBE (Disabled Veteran Business Enterprise), SBE (Small Business Enterprise), NP (Non-Profit), or MB (Micro Business).

    10. Field Name: acquisitionType
        Field Description: Category of the acquisition, such as it goods, non-it goods, it services, etc.

    11. Field Name: acquisitionMethod
        Field Description: The specific method or process used to acquire the items, varying by organizational context.

    12. Field Name: calCardUsed
        Field Description: Indicates whether a state-issued credit card (CalCard) was used for the purchase. Values are "Yes" or "No".

    Line Item Fields:
    The field lineItems is an array within the purchase order document that contains the details of individual items associated with the order. Each line item includes the following fields:

    1. Field Name: itemName
      Field Description: Name of the purchased item.

    2. Field Name: itemDescription
      Field Description: Detailed description of the purchased item.

    3. Field Name: itemDescriptionUUID
      Field Description: Unique identifier for the item description, used for normalization.

    4. Field Name: quantity
      Field Description: Number of units purchased for this line item.

    5. Field Name: unitPrice
      Field Description: Cost per unit of the item.

    6. Field Name: totalPrice
      Field Description: Total cost for the line item, excluding additional charges like taxes and shipping.

    7. Field Name: normalizedUNSPSC
      Field Description: Normalized code from the United Nations Standard Products and Services Code (UNSPSC) for classifying products or services.

    8. Field Name: commodityTitle
      Field Description: Title associated with the normalized UNSPSC.

    9. Field Name: commodityTitleUUID
      Field Description: Unique identifier for the commodityTitle, used for normalization.
    """

    FEW_SHOT_EXAMPLE_1 = {
        "query": "Total number of orders created during Q1 of 2013.",
        "pipeline": [
            {
                "$match": {
                    "creationDate": {
                        "$gte": datetime(2013, 1, 1, 0, 0, 0),
                        "$lte": datetime(2013, 3, 31, 23, 59, 59),
                    }
                }
            },
            {"$count": "total_orders"},
        ],
    }

    FEW_SHOT_EXAMPLE_2 = {
        "query": "Calculate the total sum of all item prices in 2013.",
        "pipeline": [
            {
                "$match": {
                    "creationDate": {
                        "$gte": datetime(2013, 1, 1, 0, 0, 0),
                        "$lte": datetime(2013, 12, 31, 23, 59, 59),
                    }
                }
            },
            {
                "$addFields": {
                    "numericTotalPrice": {
                        "$convert": {
                            "input": {"$substr": ["$totalPrice", 1, -1]},
                            "to": "double",
                            "onError": 0,
                            "onNull": 0,
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_price_sum": {"$sum": "$numericTotalPrice"},
                }
            },
            {"$project": {"_id": 0, "total_price_sum": 1}},
        ],
    }

    FEW_SHOT_EXAMPLE_3 = {
        "query": "Identification of the quarter with the highest spending.",
        "pipeline": [
            {
                "$addFields": {
                    "numericTotalPrice": {
                        "$convert": {
                            "input": {"$substr": ["$totalPrice", 1, -1]},
                            "to": "double",
                            "onError": 0,
                            "onNull": 0,
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$creationDate"},
                        "quarter": {
                            "$ceil": {"$divide": [{"$month": "$creationDate"}, 3]}
                        },
                    },
                    "total_spending": {"$sum": "$numericTotalPrice"},
                }
            },
            {"$sort": {"total_spending": -1}},
            {"$limit": 1},
            {
                "$project": {
                    "quarter": "$_id.quarter",
                    "year": "$_id.year",
                    "total_spending": 1,
                    "_id": 0,
                }
            },
        ],
    }

    FEW_SHOT_EXAMPLE_4 = {
        "query": "Total spending grouped by Acquisition Type in 2013.",
        "pipeline": [
            {
                "$match": {
                    "creationDate": {
                        "$gte": datetime(2013, 1, 1, 0, 0, 0),
                        "$lte": datetime(2013, 12, 31, 23, 59, 59),
                    }
                }
            },
            {
                "$addFields": {
                    "numeric_price": {
                        "$convert": {
                            "input": {"$substr": ["$totalPrice", 1, -1]},
                            "to": "double",
                            "onError": 0,
                            "onNull": 0,
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$acquisitionType",
                    "total_spending": {"$sum": "$numeric_price"},
                }
            },
            {"$sort": {"total_spending": -1}},
        ],
    }

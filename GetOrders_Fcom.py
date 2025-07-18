import requests
import urllib.parse
from hashlib import sha256
from hmac import HMAC
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import pandas as pd
import os
import json


# --- CONFIGURACIÓN GLOBAL ---
API_KEY = ''
USER_ID = '
API_URL = 'https://sellercenter-api.falabella.com/'
VERSION = '1.0'
FORMAT = 'XML'
XML_FILE = 'respuesta.xml'
EXCEL_FILE = 'pedidos.xlsx'

def generar_firma(params: dict, api_key: str) -> str:
    """Genera la firma HMAC-SHA256."""
    sorted_query = urllib.parse.urlencode(sorted(params.items()))
    return HMAC(api_key.encode('utf-8'), sorted_query.encode('utf-8'), sha256).hexdigest()
  
def construir_url(api_key: str, action: str, extra_params: dict = None) -> str:
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    params = {
        'Action': action,
        'Format': FORMAT,
        'Timestamp': timestamp,
        'UserID': USER_ID,
        'Version': VERSION,
    }
    if extra_params:
        params.update(extra_params)
    params['Signature'] = generar_firma(params, api_key)
    return f"{API_URL}?{urllib.parse.urlencode(params)}"

def obtener_ordenes() -> pd.DataFrame:
    """Obtiene los pedidos (GetOrders) y los retorna como DataFrame"""
    url = construir_url(API_KEY, 'GetOrders')
    response = requests.get(url)
    root = ET.fromstring(response.text)
    orders = root.find('.//Orders')
    data = []

    for order in orders.findall('Order'):
        extra_attr_raw = order.findtext('ExtraAttributes')
        extra_attr = {}
        if extra_attr_raw:
            try:
                extra_attr = json.loads(extra_attr_raw)
            except json.JSONDecodeError:
                pass  # Puedes loguear si deseas

        # Crear el diccionario base
        row = {
            'OrderId': order.findtext('OrderId'),
            'CustomerFirstName': order.findtext('CustomerFirstName'),
            'CustomerLastName': order.findtext('CustomerLastName'),
            'OrderNumber': order.findtext('OrderNumber'),
            'PaymentMethod': order.findtext('PaymentMethod'),
            'Remarks': order.findtext('Remarks'),
            'DeliveryInfo': order.findtext('DeliveryInfo'),
            'Price': order.findtext('Price'),
            'GiftOption': order.findtext('GiftOption'),
            'GiftMessage': order.findtext('GiftMessage'),
            'VoucherCode': order.findtext('VoucherCode'),
            'CreatedAt': order.findtext('CreatedAt'),
            'UpdatedAt': order.findtext('UpdatedAt'),
            'AddressUpdatedAt': order.findtext('AddressUpdatedAt'),
            # Billing address
            'AddressBillingFirstName': order.findtext('AddressBilling/FirstName'),
            'AddressBillingLastName': order.findtext('AddressBilling/LastName'),
            'AddressBillingAddress1': order.findtext('AddressBilling/Address1'),
            'AddressBillingAddress2': order.findtext('AddressBilling/Address2'),
            'AddressBillingAddress3': order.findtext('AddressBilling/Address3'),
            'AddressBillingAddress4': order.findtext('AddressBilling/Address4'),
            'AddressBillingAddress5': order.findtext('AddressBilling/Address5'),
            'AddressBillingCustomerEmail': order.findtext('AddressBilling/CustomerEmail'),
            'AddressBillingCity': order.findtext('AddressBilling/City'), 
            'AddressBillingWard': order.findtext('AddressBilling/Ward'),
            'AddressBillingRegion': order.findtext('AddressBilling/Region'), 
            'AddressBillingPostCode': order.findtext('AddressBilling/PostCode'),
            'AddressBillingCountry': order.findtext('AddressBilling/Country'), 
            'AddressBillingPhone': order.findtext('AddressBilling/Phone'),
            'AddressBillingPhone2': order.findtext('AddressBilling/Phone2'), 
            # Shipping address
            'AddressShippingFirstName': order.findtext('AddressShipping/FirstName'),
            'AddressShippingLastName': order.findtext('AddressShipping/LastName'),
            'AddressShippingPhone': order.findtext('AddressShipping/Phone'),
            'AddressShippingPhone2': order.findtext('AddressShipping/Phone2'),
            'AddressShippingAddress1': order.findtext('AddressShipping/Address1'),
            'AddressShippingAddress2': order.findtext('AddressShipping/Address2'),
            'AddressShippingAddress3': order.findtext('AddressShipping/Address3'),
            'AddressShippingAddress4': order.findtext('AddressShipping/Address4'),
            'AddressShippingAddress5': order.findtext('AddressShipping/Address5'), 
            'AddressShippingCustomerEmail': order.findtext('AddressShipping/CustomerEmail'),            
            'AddressShippingCity': order.findtext('AddressShipping/City'),
            'AddressShippingWard': order.findtext('AddressShipping/Ward'),
            'AddressShippingRegion': order.findtext('AddressShipping/Region'),
            'AddressShippingCountry': order.findtext('AddressShipping/Country'),
            'AddressShippingPostCode': order.findtext('AddressShipping/PostCode'),

            'NationalRegistrationNumber': order.findtext('NationalRegistrationNumber'),
            'ItemsCount': order.findtext('ItemsCount'),
            'PromisedShippingTime': order.findtext('PromisedShippingTime'),
            # ExtraBillingAttributes
            'ExtraBillingAttributesLegalId': order.findtext('ExtraBillingAttributes/LegalId'),
            'ExtraBillingAttributesFiscalPerson': order.findtext('ExtraBillingAttributes/FiscalPerson'),
            'ExtraBillingAttributesDocumentType': order.findtext('ExtraBillingAttributes/DocumentType'),
            'ExtraBillingAttributesReceiverRegion': order.findtext('ExtraBillingAttributes/ReceiverRegion'),
            'ExtraBillingAttributesReceiverAddress': order.findtext('ExtraBillingAttributes/ReceiverAddress'),
            'ExtraBillingAttributesReceiverPostcode': order.findtext('ExtraBillingAttributes/ReceiverPostcode'),
            'ExtraBillingAttributesReceiverLegalName': order.findtext('ExtraBillingAttributes/ReceiverLegalName'),
            'ExtraBillingAttributesReceiverMunicipality': order.findtext('ExtraBillingAttributes/ReceiverMunicipality'),
            'ExtraBillingAttributesReceiverTypeRegimen': order.findtext('ExtraBillingAttributes/ReceiverTypeRegimen'),
            'ExtraBillingAttributesCustomerVerifierDigit': order.findtext('ExtraBillingAttributes/CustomerVerifierDigit'),
            'ExtraBillingAttributesReceiverPhonenumber': order.findtext('ExtraBillingAttributes/ReceiverPhonenumber'),
            'ExtraBillingAttributesReceiverEmail': order.findtext('ExtraBillingAttributes/ReceiverEmail'),
            'ExtraBillingAttributesReceiverLocality': order.findtext('ExtraBillingAttributes/ReceiverLocality'),

            'InvoiceRequired': order.findtext('InvoiceRequired'),
            'OperatorCode': order.findtext('OperatorCode'),
            'ShippingType': order.findtext('ShippingType'),
            'GrandTotal': order.findtext('GrandTotal'),
            'ProductTotal': order.findtext('ProductTotal'),
            'TaxAmount': order.findtext('TaxAmount'),
            'ShippingFeeTotal': order.findtext('ShippingFeeTotal'),
            'ShippingTax': order.findtext('ShippingTax'),
            'Voucher': order.findtext('Voucher'),
            'Status': order.findtext('Statuses/Status'),    
        }
        # Agregar los campos de ExtraAttributes
        for key, value in extra_attr.items():
            row[f'ExtraAttributes{key}'] = value

        data.append(row)

    return pd.DataFrame(data)

def obtener_items(order_ids: list) -> pd.DataFrame:
    """Obtiene ítems por pedido (GetMultipleOrderItems) y los retorna como DataFrame"""
    all_items = []

    for order_id in order_ids:
        extra_params = {'OrderIdList': order_id}
        url = construir_url(API_KEY, 'GetMultipleOrderItems', extra_params)
        response = requests.get(url, headers={"accept": "application/xml"})

        try:
            root = ET.fromstring(response.text)
            order_items = root.find('.//OrderItems')
            if order_items is not None:
                for item in order_items.findall('OrderItem'):
                    row = {
                        'OrderId': item.findtext('OrderId'),
                        'OrderItemId': item.findtext('OrderItemId'),
                        'ShopId': item.findtext('ShopId'),
                        'Name': item.findtext('Name'),
                        'Sku': item.findtext('Sku'),
                        'Variation': item.findtext('Variation'),
                        'ShopSku': item.findtext('ShopSku'),
                        'ShippingType': item.findtext('ShippingType'),
                        'Currency': item.findtext('Currency'),
                        'VoucherCode': item.findtext('VoucherCode'),
                        'Status': item.findtext('Status'),
                        'IsProcessable': item.findtext('IsProcessable'),
                        'ShipmentProvider': item.findtext('ShipmentProvider'),
                        'IsDigital': item.findtext('IsDigital'),
                        'DigitalDeliveryInfo': item.findtext('DigitalDeliveryInfo'),
                        'TrackingCode': item.findtext('TrackingCode'),
                        'TrackingCodePre': item.findtext('TrackingCodePre'),
                        'Reason': item.findtext('Reason'),
                        'ReasonDetail': item.findtext('ReasonDetail'),
                        'PurchaseOrderId': item.findtext('PurchaseOrderId'),
                        'PurchaseOrderNumber': item.findtext('PurchaseOrderNumber'),
                        'PackageId': item.findtext('PackageId'),
                        'PromisedShippingTime': item.findtext('PromisedShippingTime'),
                        'ShippingProviderType': item.findtext('ShippingProviderType'),
                        'CreatedAt': item.findtext('CreatedAt'),
                        'UpdatedAt': item.findtext('UpdatedAt'),
                        'Vouchers': item.findtext('Vouchers'),
                        'SalesType': item.findtext('SalesType'),
                        'ReturnStatus': item.findtext('ReturnStatus'),
                        'WalletCredits': item.findtext('WalletCredits'),
                        'ItemPrice': item.findtext('ItemPrice'),
                        'PaidPrice': item.findtext('PaidPrice'),
                        'TaxAmount': item.findtext('TaxAmount'),
                        'CodCollectableAmount': item.findtext('CodCollectableAmount'),
                        'ShippingAmount': item.findtext('ShippingAmount'),
                        'ShippingServiceCost': item.findtext('ShippingServiceCost'),
                        'ShippingTax': item.findtext('ShippingTax'),
                        'VoucherAmount': item.findtext('VoucherAmount'),
                        'Quantity': item.findtext('Quantity'),
                    }
                    all_items.append(row)
        except Exception as e:
            print(f"Error al procesar OrderId {order_id}: {e}")

    return pd.DataFrame(all_items)

def main():
    print("Obteniendo pedidos...")
    df_orders = obtener_ordenes()
    df_orders.to_excel('order.xlsx', index=False)
    print(f"{len(df_orders)} pedidos encontrados.")

    print("Obteniendo ítems por pedido...")
    order_ids = df_orders['OrderId'].dropna().unique().tolist()
    df_items = obtener_items(order_ids)
    df_items.to_excel('Items.xlsx', index=False)
    print(f"{len(df_items)} ítems encontrados.")

    print("Combinando pedidos con ítems...")
    df_final = df_items.merge(df_orders, on='OrderId', how='left')

    print(f"Guardando en archivo Excel: {EXCEL_FILE}")
    df_final.to_excel(EXCEL_FILE, index=False)
    print("Proceso completado.")

if __name__ == '__main__':
    main()

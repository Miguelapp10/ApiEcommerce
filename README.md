# ApiEcommerce

# 🧾 Descarga y Consolidación de Pedidos desde Seller Center API (Fcom)

Este script en Python permite conectarse a la API de **Seller Center de Fcom**, obtener información detallada de pedidos (`GetOrders`) e ítems por pedido (`GetMultipleOrderItems`), y consolidar todo en un único archivo Excel.

## 📦 ¿Qué hace este script?

1. Autentica con HMAC-SHA256 a la API de Seller Center.
2. Consulta todos los pedidos disponibles usando la acción `GetOrders`.
3. Consulta los ítems asociados a cada pedido usando `GetMultipleOrderItems`.
4. Une la información de pedidos e ítems en un solo `DataFrame`.
5. Exporta tres archivos Excel:
   - `order.xlsx`: Contiene el detalle de los pedidos.
   - `Items.xlsx`: Contiene los ítems individuales por pedido.
   - `pedidos.xlsx`: Consolidado de ambos anteriores.

## 📁 Requisitos

Instala las dependencias necesarias:

```bash
pip install pandas requests openpyxl

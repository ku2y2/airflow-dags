{{ config(materialized='view') }}

with source_data as (
    select
        1 as order_id,
        'customer_1' as customer_id,
        '2023-01-01' as order_date,
        100.00 as amount,
        'completed' as status

    union all

    select
        2 as order_id,
        'customer_2' as customer_id,
        '2023-01-02' as order_date,
        200.00 as amount,
        'pending' as status

    union all

    select
        3 as order_id,
        'customer_1' as customer_id,
        '2023-01-03' as order_date,
        150.00 as amount,
        'completed' as status
)

select
    order_id,
    customer_id,
    cast(order_date as date) as order_date,
    amount,
    status
from source_data
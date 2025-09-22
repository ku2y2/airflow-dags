{{ config(materialized='table') }}

with orders as (
    select * from {{ ref('stg_orders') }}
),

customer_summary as (
    select
        customer_id,
        count(*) as total_orders,
        sum(amount) as total_amount,
        avg(amount) as avg_amount,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date
    from orders
    where status = 'completed'
    group by customer_id
)

select * from customer_summary
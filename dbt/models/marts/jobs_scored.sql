with staged as (
    select * from {{ ref('stg_jobs') }}
),

deduped as (
    select *,
        row_number() over (
            partition by lower(trim(title)), lower(trim(company))
            order by score desc, run_date desc
        ) as row_num
    from staged
    where score >= 15
),

final as (
    select
        id,
        run_date,
        source,
        source_job_id,
        company,
        title,
        location,
        start_date,
        link,
        score,
        current_date - cast(run_date as date) as scraped_days_ago
    from deduped
    where row_num = 1
)

select * from final
order by score desc

with source as (
    select * from jobs_sqlite.main.jobs
),

staged as (
    select
        id,
        run_date,
        source,
        source_job_id,
        trim(company)                    as company,
        trim(title)                      as title,
        trim(location)                   as location,
        start_date,
        link,
        cast(score as double)            as score,
        trim(description)                as description
    from source
    where title is not null
      and source is not null
      and score is not null
)

select * from staged

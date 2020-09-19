# Track cyclone info

## Getting started
- Unzip or clone the repository
- Run commands
    - Build images
        ```
        docker-compose build
        ```
    - Run containers
        ```
        docker-compose up
        ```

## Making requests
- Check out attached postman collection

    - ### Get oceans
        - #### GET - `/oceans`
            - Retrieve list of oceans

    - ### Get cyclones
        - #### GET - `/cyclones`
            - Retrieve list of cyclones

    - ### Get cyclone activities
        - #### GET - `/activity`
            - Retrieve tracked cyclone activity information

                Param | Type | Necessity | Description
                --- | --- | --- | ---
                start_time | string | Optional | Datetime string in format (Y-m-d-H:M)
                end_time | string | Optional | Datetime string in format (Y-m-d-H:M)
                ocean | string | Optional | Ocean string

## Services
- PostgreSQL
    - Database to persist information
- Crawler
    - Scheduled task (cron job) which periodically pulls data from cyclone information website and inserts into database
- Web
    - Web service which exposes endpoints for user to retrieve information

## Note
- Refer to `src/db/db.py` for database schema
- Crawler is configured to pull info every second for testing
- Uncomment/comment 
    ```python
    # schedule.every(EVERY_NTH_HOUR).hour.do(crawl)
    schedule.every(EVERY_NTH_HOUR).second.do(crawl)
    ``` 
    in `src/crawler/crawler.py` to configure correct interval accordingly

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import snowflake.connector
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import traceback
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


load_dotenv()

app = FastAPI()


SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "BOTFOLIO_WH")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "BOTFOLIO_DB")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "APP")


def setup_jobs_endpoints(app):
    
    
    
    class JobFilter(BaseModel):
        role: Optional[str] = None
        time_filter: Optional[str] = None
        seniority_level: Optional[str] = None
        employment_type: Optional[str] = None
        action: Optional[str] = None  
    
    class InterviewPrepData(BaseModel):
        job_role: str
        skills: List[str]
        job_url: str
    
    class JobsRequest(BaseModel):
        filter: Optional[JobFilter] = None
        interview_prep: Optional[InterviewPrepData] = None
    
    
    JOBS_CACHE = {
        "data": None,
        "timestamp": None
    }
    
    def get_snowflake_connection():
        
        try:
            logger.info(f"Connecting to Snowflake with account: {SNOWFLAKE_ACCOUNT}, user: {SNOWFLAKE_USER}, warehouse: {SNOWFLAKE_WAREHOUSE}")
            conn = snowflake.connector.connect(
                user=SNOWFLAKE_USER,
                password=SNOWFLAKE_PASSWORD,
                account=SNOWFLAKE_ACCOUNT,
                warehouse=SNOWFLAKE_WAREHOUSE,
                database=SNOWFLAKE_DATABASE,
                schema=SNOWFLAKE_SCHEMA
            )
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Failed to connect to Snowflake: {str(e)}")

    def get_all_jobs_from_snowflake():
        
        conn = get_snowflake_connection()
        
        try:
            cursor = conn.cursor()
            
            
            query = """
            SELECT POSTED_DATE, JOB_ROLE, TITLE, COMPANY, SENIORITY_LEVEL, EMPLOYMENT_TYPE, SKILLS, URL
            FROM JOB_HISTORY
            WHERE POSTED_DATE >= DATEADD(hour, -5, CURRENT_TIMESTAMP())
            ORDER BY POSTED_DATE DESC
            """
            
            logger.info(f"Executing Snowflake query: {query}")
            cursor.execute(query)
            
            
            results = cursor.fetchall()
            logger.info(f"Query returned {len(results)} results")
            
            
            column_names = ["POSTED_DATE", "JOB_ROLE", "TITLE", "COMPANY", "SENIORITY_LEVEL", "EMPLOYMENT_TYPE", "SKILLS", "URL"]
            df = pd.DataFrame(results, columns=column_names)
            
            return df
        
        except Exception as e:
            logger.error(f"Error fetching jobs from Snowflake: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error fetching jobs from Snowflake: {str(e)}")
        finally:
            conn.close()

    def filter_jobs(jobs_df, role=None, time_filter=None, seniority_level=None, employment_type=None):
        """
        Filter jobs data locally (no Snowflake query)
        """
        if jobs_df is None or jobs_df.empty:
            return pd.DataFrame(columns=["POSTED_DATE", "JOB_ROLE", "TITLE", "COMPANY", "SENIORITY_LEVEL", "EMPLOYMENT_TYPE", "SKILLS", "URL"])
        
        
        filtered_df = jobs_df.copy()
        
        
        if role:
            filtered_df = filtered_df[filtered_df["JOB_ROLE"] == role]
        
        
        if time_filter:
            hours_map = {
                "30min": 0.5,
                "1hr": 1,
                "2hr": 2,
                "3hr": 3,
                "4hr": 4
            }
            
            if time_filter in hours_map:
                hours = hours_map[time_filter]
                cutoff_time = datetime.now() - timedelta(hours=hours)
                filtered_df = filtered_df[filtered_df["POSTED_DATE"] >= cutoff_time]
        
        
        if seniority_level and seniority_level != "All Levels":
            filtered_df = filtered_df[filtered_df["SENIORITY_LEVEL"].fillna("Not Applicable") == seniority_level]
        
        
        if employment_type and employment_type != "All Types":
            filtered_df = filtered_df[filtered_df["EMPLOYMENT_TYPE"].fillna("Not Applicable") == employment_type]
        
        return filtered_df

    def refresh_jobs_cache():
        """Refresh the jobs cache from Snowflake"""
        try:
            logger.info("Refreshing jobs cache from Snowflake")
            JOBS_CACHE["data"] = get_all_jobs_from_snowflake()
            JOBS_CACHE["timestamp"] = datetime.now()
            logger.info(f"Cache refreshed with {len(JOBS_CACHE['data'])} jobs")
        except Exception as e:
            logger.error(f"Error refreshing jobs cache: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
   
    @app.on_event("startup")
    async def startup_event():
        """Initialize the cache on startup"""
        try:
            logger.info("Initializing jobs cache on startup")
            refresh_jobs_cache()
        except Exception as e:
            logger.error(f"Failed to initialize cache on startup: {str(e)}")
            logger.error("The application will attempt to initialize the cache on the first request")
    
    
    @app.post("/jobs-api")
    async def jobs_api(request: JobsRequest):
        """Consolidated endpoint for all job-related operations"""
        
        
        if request.filter is None:
            request.filter = JobFilter()
        
        
        action = request.filter.action or "filter"
        
        
        cache_needs_refresh = (
            JOBS_CACHE["data"] is None or
            JOBS_CACHE["timestamp"] is None or
            (datetime.now() - JOBS_CACHE["timestamp"]).seconds > 1800
        )
        
        
        if action == "status":
            return {
                "cache_exists": JOBS_CACHE["data"] is not None,
                "last_refresh": JOBS_CACHE["timestamp"].isoformat() if JOBS_CACHE["timestamp"] else None,
                "job_count": len(JOBS_CACHE["data"]) if JOBS_CACHE["data"] is not None else 0,
                "cache_age_seconds": (datetime.now() - JOBS_CACHE["timestamp"]).seconds if JOBS_CACHE["timestamp"] else None
            }
        
        
        elif action == "refresh":
            try:
                refresh_jobs_cache()
                return {"status": "success", "message": "Cache refreshed successfully"}
            except Exception as e:
                logger.error(f"Error refreshing cache: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error refreshing cache: {str(e)}")
        
        
        elif action == "interview-prep":
            if not request.interview_prep:
                raise HTTPException(status_code=400, detail="Interview prep data required for 'interview-prep' action")
            
            try:
                
                job_role = request.interview_prep.job_role
                skills = request.interview_prep.skills
                job_url = request.interview_prep.job_url
                
                logger.info(f"Interview prep requested for {job_role} with skills: {', '.join(skills)}")
                
                
                return {
                    "status": "success", 
                    "message": f"Interview preparation materials for {job_role} role with focus on {', '.join(skills)} will be available soon!"
                }
            except Exception as e:
                logger.error(f"Error in interview prep: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error processing interview prep request: {str(e)}")
        
        
        elif action == "export":
            if cache_needs_refresh:
                try:
                    refresh_jobs_cache()
                except Exception as e:
                    logger.error(f"Error refreshing cache for export: {str(e)}")
                    if JOBS_CACHE["data"] is None:
                        raise HTTPException(status_code=500, detail=f"Error exporting jobs: {str(e)}")
            
            try:
                
                filtered_df = filter_jobs(
                    JOBS_CACHE["data"],
                    role=request.filter.role,
                    time_filter=request.filter.time_filter,
                    seniority_level=request.filter.seniority_level,
                    employment_type=request.filter.employment_type
                )
                
                
                csv_str = filtered_df.to_csv(index=False)
                
                return {"csv_data": csv_str}
            
            except Exception as e:
                logger.error(f"Error exporting jobs: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error exporting jobs: {str(e)}")
        
        
        else:  
            if cache_needs_refresh:
                try:
                    refresh_jobs_cache()
                except Exception as e:
                    logger.error(f"Error refreshing cache: {str(e)}")
                   
                    if JOBS_CACHE["data"] is None:
                        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")
                    logger.warning("Using old cache data due to refresh failure")
            
            try:
                
                filtered_df = filter_jobs(
                    JOBS_CACHE["data"],
                    role=request.filter.role,
                    time_filter=request.filter.time_filter,
                    seniority_level=request.filter.seniority_level,
                    employment_type=request.filter.employment_type
                )
                
                
                jobs_list = filtered_df.to_dict(orient="records")
                
                
                for job in jobs_list:
                    if isinstance(job["POSTED_DATE"], pd.Timestamp) or isinstance(job["POSTED_DATE"], datetime):
                        job["POSTED_DATE"] = job["POSTED_DATE"].isoformat()
                
                return {"jobs": jobs_list}
            
            except Exception as e:
                logger.error(f"Error retrieving jobs: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error retrieving jobs: {str(e)}")


    
setup_jobs_endpoints(app)
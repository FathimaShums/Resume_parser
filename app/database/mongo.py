import os
import datetime
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Load env variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "resume_parser")

class MongoDBClient:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False
        self.connect()

    def connect(self) -> bool:
        if not MONGODB_URI:
            print("WARNING: MONGODB_URI not set in environment.")
            self.connected = False
            return False
            
        try:
            # Set a 3-second timeout for server selection so we don't hang if unreachable
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
            # Trigger a connection attempt
            self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            self.collection = self.db["parsed_resumes"]
            self.connected = True
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"WARNING: Failed to connect to MongoDB: {str(e)}")
            self.connected = False
            return False
        except Exception as e:
            print(f"WARNING: Unexpected error connecting to MongoDB: {str(e)}")
            self.connected = False
            return False

    def is_connected(self) -> bool:
        # Re-check or return status
        if not self.connected:
            return self.connect()
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            self.connected = False
            return False

    def save_resume(self, filename: str, parsed_result: Dict[str, Any], raw_text: str) -> Optional[str]:
        """
        Saves a parsed resume document to the database.
        Returns the inserted document's string ID if successful, else None.
        """
        if not self.is_connected():
            return None
            
        try:
            doc = {
                "filename": filename,
                "uploaded_at": datetime.datetime.utcnow(),
                "parsed_data": parsed_result.get("parsed_data", {}),
                "completeness_score": parsed_result.get("completeness_score", 0.0),
                "confidence_score": parsed_result.get("confidence_score", 0.0),
                "raw_text_preview": raw_text[:500] if raw_text else ""
            }
            res = self.collection.insert_one(doc)
            return str(res.inserted_id)
        except Exception as e:
            print(f"Error saving resume: {str(e)}")
            return None

    def fetch_all_resumes(self) -> List[Dict[str, Any]]:
        """
        Fetches all parsed resume records from the collection.
        """
        if not self.is_connected():
            return []
            
        try:
            cursor = self.collection.find().sort("uploaded_at", -1)
            results = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                results.append(doc)
            return results
        except Exception as e:
            print(f"Error fetching resumes: {str(e)}")
            return []

    def fetch_resume_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches a single resume record by its string ObjectId.
        """
        if not self.is_connected():
            return None
            
        try:
            doc = self.collection.find_one({"_id": ObjectId(doc_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return doc
            return None
        except Exception as e:
            print(f"Error fetching resume {doc_id}: {str(e)}")
            return None

    def delete_resume(self, doc_id: str) -> bool:
        """
        Deletes a single resume record by its string ObjectId.
        """
        if not self.is_connected():
            return False
            
        try:
            res = self.collection.delete_one({"_id": ObjectId(doc_id)})
            return res.deleted_count > 0
        except Exception as e:
            print(f"Error deleting resume {doc_id}: {str(e)}")
            return False

# Singleton instance
db_client = MongoDBClient()

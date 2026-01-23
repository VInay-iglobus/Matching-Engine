"""
Database Module
Handles SQLite database operations for storing and retrieving matching results
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json
import pandas as pd

# Database path in same directory
DB_PATH = Path("data.db")

class DatabaseManager:
    """Manage SQLite database for matching results"""
    
    def __init__(self, db_path=DB_PATH):
        """Initialize database manager"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            raise Exception(f"Database connection failed: {e}")
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Single Match Results Table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS single_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL DEFAULT 'unknown',
                resume_name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                overall_score INTEGER NOT NULL,
                experience_score INTEGER NOT NULL,
                education_score INTEGER NOT NULL,
                skills_score INTEGER NOT NULL,
                experience_met BOOLEAN NOT NULL,
                education_met BOOLEAN NOT NULL,
                skills_met BOOLEAN NOT NULL,
                skills_percentage INTEGER,
                assessment TEXT NOT NULL,
                summary TEXT,
                resume_data JSON,
                jd_data JSON,
                matching_result JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
            
            # Batch Results Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS batch_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT NOT NULL DEFAULT 'unknown',
                    batch_id TEXT UNIQUE NOT NULL,
                    job_title TEXT NOT NULL,
                    total_resumes INTEGER NOT NULL,
                    total_valid INTEGER NOT NULL,
                    average_score REAL NOT NULL,
                    highest_score INTEGER NOT NULL,
                    lowest_score INTEGER NOT NULL,
                    jd_data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Batch Candidates Table (Individual candidates in batch)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS batch_candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT NOT NULL DEFAULT 'unknown',
                    batch_id TEXT NOT NULL,
                    rank INTEGER NOT NULL,
                    resume_name TEXT NOT NULL,
                    overall_score INTEGER NOT NULL,
                    experience_score INTEGER NOT NULL,
                    education_score INTEGER NOT NULL,
                    skills_score INTEGER NOT NULL,
                    experience_met BOOLEAN NOT NULL,
                    education_met BOOLEAN NOT NULL,
                    skills_met BOOLEAN NOT NULL,
                    skills_percentage INTEGER,
                    assessment TEXT NOT NULL,
                    resume_data JSON,
                    matching_result JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (batch_id) REFERENCES batch_results(batch_id)
                )
            ''')
            
            # Analytics Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_type TEXT NOT NULL,
                    total_matches INTEGER DEFAULT 0,
                    average_score REAL DEFAULT 0,
                    excellent_count INTEGER DEFAULT 0,
                    good_count INTEGER DEFAULT 0,
                    needs_review_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            print(f"✅ Database initialized at {self.db_path}")
        
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            conn.rollback()
        
        finally:
            conn.close()
    
    # ==================== SINGLE MATCH OPERATIONS ====================
    
    def save_single_match(self, user_email, resume_name, job_title, resume_data, jd_data, matching_result):
        """
        Save single match result to database
        
        Args:
            user_email (str): Email of user who created the match
            resume_name (str): Resume file name
            job_title (str): Job title
            resume_data (dict): Extracted resume data
            jd_data (dict): Extracted JD data
            matching_result (dict): Matching result with scores
        
        Returns:
            int: Row ID of inserted record
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            criteria = matching_result.get('criteriaAnalysis', {})
            scores = matching_result.get('sectionScores', {})
            
            cursor.execute('''
                INSERT INTO single_matches (
                    user_email,resume_name, job_title, overall_score,
                    experience_score, education_score, skills_score,
                    experience_met, education_met, skills_met,
                    skills_percentage, assessment, summary,
                    resume_data, jd_data, matching_result
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_email,
                resume_name,
                job_title,
                matching_result.get('overallScore', 0),
                scores.get('experienceMatch', 0),
                scores.get('educationMatch', 0),
                scores.get('skillsMatch', 0),
                criteria.get('experienceMatch', {}).get('met', False),
                criteria.get('educationMatch', {}).get('met', False),
                criteria.get('skillsMatch', {}).get('met', False),
                criteria.get('skillsMatch', {}).get('percentage', 0),
                matching_result.get('assessment', {}).get('text', ''),
                matching_result.get('summary', ''),
                json.dumps(resume_data),
                json.dumps(jd_data),
                json.dumps(matching_result)
            ))
            
            conn.commit()
            row_id = cursor.lastrowid
            print(f"✅ Single match saved (ID: {row_id})")
            return row_id
        
        except Exception as e:
            print(f"❌ Error saving single match: {e}")
            conn.rollback()
            return None
        
        finally:
            conn.close()
    
    def get_single_match(self, match_id):
        """Get single match result by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM single_matches WHERE id = ?', (match_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        
        finally:
            conn.close()
    
    def get_all_single_matches(self, user_email, limit=100):
        """Get all single match results for a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, resume_name, job_title, overall_score, 
                       assessment, created_at 
                FROM single_matches 
                WHERE user_email = ?
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_email, limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        finally:
            conn.close()
    
    def delete_single_match(self, match_id):
        """Delete single match record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM single_matches WHERE id = ?', (match_id,))
            conn.commit()
            print(f"✅ Match {match_id} deleted")
            return True
        
        except Exception as e:
            print(f"❌ Error deleting match: {e}")
            conn.rollback()
            return False
        
        finally:
            conn.close()
    
    # ==================== BATCH MATCH OPERATIONS ====================
    
    def save_batch_result(self, user_email, batch_id, job_title, results, jd_data):
        """
        Save batch processing result
        
        Args:
            user_email (str): Email of user who created the batch
            batch_id (str): Unique batch identifier
            job_title (str): Job title
            results (list): List of candidate results
            jd_data (dict): Job description data
        
        Returns:
            bool: Success status
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            scores = [r['matching_result']['overallScore'] for r in results]
            
            cursor.execute('''
                INSERT INTO batch_results (
                    user_email, batch_id, job_title, total_resumes, total_valid,
                    average_score, highest_score, lowest_score, jd_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_email,
                batch_id,
                job_title,
                len(results),
                len(results),
                sum(scores) / len(scores) if scores else 0,
                max(scores) if scores else 0,
                min(scores) if scores else 0,
                json.dumps(jd_data)
            ))
            
            # Insert individual candidates
            for rank, result in enumerate(results, 1):
                self.save_batch_candidate(
                    batch_id, rank, result
                )
            
            conn.commit()
            print(f"✅ Batch result saved (ID: {batch_id})")
            return True
        
        except Exception as e:
            print(f"❌ Error saving batch result: {e}")
            conn.rollback()
            return False
        
        finally:
            conn.close()
    
    def save_batch_candidate(self, user_email,  batch_id, rank, result):
        """Save individual candidate in batch"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            criteria = result['matching_result'].get('criteriaAnalysis', {})
            scores = result['matching_result'].get('sectionScores', {})
            
            cursor.execute('''
                INSERT INTO batch_candidates (
                    user_email, batch_id, rank, resume_name, overall_score,
                    experience_score, education_score, skills_score,
                    experience_met, education_met, skills_met,
                    skills_percentage, assessment,
                    resume_data, matching_result
                ) VALUES (user_email, batch_id, rank, result['filename'],)
            ''', 
                batch_id,
                rank,
                result['filename'],
                result['matching_result'].get('overallScore', 0),
                scores.get('experienceMatch', 0),
                scores.get('educationMatch', 0),
                scores.get('skillsMatch', 0),
                criteria.get('experienceMatch', {}).get('met', False),
                criteria.get('educationMatch', {}).get('met', False),
                criteria.get('skillsMatch', {}).get('met', False),
                criteria.get('skillsMatch', {}).get('percentage', 0),
                result['matching_result'].get('assessment', {}).get('text', ''),
                json.dumps(result['resume_data']),
                json.dumps(result['matching_result'])
            )
            
            conn.commit()
        
        except Exception as e:
            print(f"❌ Error saving batch candidate: {e}")
            conn.rollback()
        
        finally:
            conn.close()
    
    def get_batch_result(self, user_email,batch_id):
        """Get batch result with all candidates"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get batch info
            cursor.execute('SELECT * FROM batch_results WHERE batch_id = ?', (batch_id, user_email,))
            batch_row = cursor.fetchone()
            
            if not batch_row:
                return None
            
            batch_data = dict(batch_row)
            
            # Get candidates
            cursor.execute('''
                SELECT * FROM batch_candidates 
                WHERE batch_id = ? 
                ORDER BY rank ASC
            ''', (batch_id,))
            
            candidates = [dict(row) for row in cursor.fetchall()]
            batch_data['candidates'] = candidates
            
            return batch_data
        
        finally:
            conn.close()
    
    def get_all_batch_results(self, limit=50):
        """Get all batch results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, batch_id, job_title, total_resumes, 
                       average_score, highest_score, created_at 
                FROM batch_results
                WHERE user_email =?
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_email, limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        finally:
            conn.close()
    
    def delete_batch_result(self, batch_id):
        """Delete batch result and all candidates"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM batch_candidates WHERE batch_id = ?', (batch_id,))
            cursor.execute('DELETE FROM batch_results WHERE batch_id = ?', (batch_id,))
            conn.commit()
            print(f"✅ Batch {batch_id} deleted")
            return True
        
        except Exception as e:
            print(f"❌ Error deleting batch: {e}")
            conn.rollback()
            return False
        
        finally:
            conn.close()
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    def update_analytics(self):
        """Update analytics table with current statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Single matches analytics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    AVG(overall_score) as avg_score,
                    SUM(CASE WHEN overall_score >= 70 THEN 1 ELSE 0 END) as excellent,
                    SUM(CASE WHEN overall_score >= 50 AND overall_score < 70 THEN 1 ELSE 0 END) as good,
                    SUM(CASE WHEN overall_score < 50 THEN 1 ELSE 0 END) as needs_review
                FROM single_matches
            ''')
            
            row = cursor.fetchone()
            if row:
                cursor.execute('''
                    INSERT OR REPLACE INTO analytics 
                    (match_type, total_matches, average_score, excellent_count, good_count, needs_review_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    'single',
                    row[0] or 0,
                    row[1] or 0,
                    row[2] or 0,
                    row[3] or 0,
                    row[4] or 0
                ))
            
            conn.commit()
            print("✅ Analytics updated")
        
        except Exception as e:
            print(f"❌ Error updating analytics: {e}")
            conn.rollback()
        
        finally:
            conn.close()
    
    def get_analytics(self, match_type='single'):
        """Get analytics for dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM analytics WHERE match_type = ?
            ''', (match_type,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
        
        finally:
            conn.close()
    
    # ==================== REPORTING OPERATIONS ====================
    
    def get_dashboard_stats(self):
        """Get overall dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Single matches stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_single,
                    AVG(overall_score) as avg_single_score,
                    MAX(overall_score) as max_single_score
                FROM single_matches
                           WHERE user_email =? 
            ''', (user_email,))
            
            row = cursor.fetchone()
            stats['single_matches'] = {
                'total': row[0] or 0,
                'average_score': round(row[1], 1) if row[1] else 0,
                'highest_score': row[2] or 0
            }
            
            # Batch results stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_batch,
                    AVG(average_score) as avg_batch_score
                FROM batch_results
                WHERE user_email = ?
            ''', (user_email,))
            
            row = cursor.fetchone()
            stats['batch_results'] = {
                'total': row[0] or 0,
                'average_score': round(row[1], 1) if row[1] else 0
            }
            
            # Total candidates evaluated
            cursor.execute('''
                SELECT COUNT(*) FROM single_matches
                WHERE user_email = ?    
                UNION ALL 
                SELECT COUNT(*) FROM batch_candidates
                WHERE user_email = ?
            ''',(user_email, user_email,))

            stats['total_candidates'] = sum(r[0] for r in cursor.fetchall())
            
            return stats
        
        finally:
            conn.close()
    
    def export_to_dataframe(self, query_type='single'):
        """Export results to pandas DataFrame"""
        conn = self.get_connection()
        
        try:
            if query_type == 'single':
                df = pd.read_sql_query('''
                    SELECT resume_name, job_title, overall_score, 
                           assessment, created_at 
                    FROM single_matches 
                    ORDER BY created_at DESC
                ''', conn)
            
            elif query_type == 'batch':
                df = pd.read_sql_query('''
                    SELECT batch_id, job_title, total_resumes, 
                           average_score, highest_score, created_at 
                    FROM batch_results 
                    ORDER BY created_at DESC
                ''', conn)
            
            else:
                df = None
            
            return df
        
        finally:
            conn.close()
    
    def clear_old_data(self, days=90):
        """Clear data older than specified days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM single_matches 
                WHERE created_at < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            cursor.execute('''
                DELETE FROM batch_results 
                WHERE created_at < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            conn.commit()
            print(f"✅ Data older than {days} days deleted")
            return True
        
        except Exception as e:
            print(f"❌ Error clearing old data: {e}")
            conn.rollback()
            return False
        
        finally:
            conn.close()
    
    def get_database_size(self):
        """Get database file size in MB"""
        try:
            size_bytes = self.db_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            return round(size_mb, 2)
        
        except Exception as e:
            print(f"❌ Error getting database size: {e}")
            return 0
    
    def backup_database(self, backup_path=None):
        """Backup database to another location"""
        if backup_path is None:
            backup_path = Path(f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        
        try:
            import shutil
            shutil.copy(self.db_path, backup_path)
            print(f"✅ Database backed up to {backup_path}")
            return True
        
        except Exception as e:
            print(f"❌ Error backing up database: {e}")
            return False


# ==================== HELPER FUNCTIONS ====================

def get_db():
    """Get or create database manager instance"""
    return DatabaseManager()

def init_db():
    """Initialize database"""
    db = DatabaseManager()
    return db
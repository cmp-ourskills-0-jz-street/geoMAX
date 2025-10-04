import sqlite3
import logging
from typing import Dict, List, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DictionaryManager:
    def __init__(self, db_path: str = "dictionaries.db"):
        self.db_path = db_path
        self._create_table()
    
    def _create_table(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS dictionaries (
                        id INTEGER PRIMARY KEY,
                        own_password TEXT NOT NULL,
                        com_password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logger.info("Таблица dictionaries создана или уже существует")
        except sqlite3.Error as e:
            logger.error(f"Ошибка при создании таблицы: {e}")
            raise
    
    def insert_dictionary(self, dictionary: Dict) -> bool:
        required_keys = {'id', 'own_password', 'com_password'}
        if not all(key in dictionary for key in required_keys):
            logger.error(f"Словарь должен содержать ключи: {required_keys}")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO dictionaries (id, own_password, com_password)
                    VALUES (?, ?, ?)
                ''', (dictionary['id'], dictionary['own_password'], dictionary['com_password']))
                conn.commit()
                logger.info(f"Словарь с id {dictionary['id']} успешно добавлен")
                return True
        except sqlite3.IntegrityError:
            logger.error(f"Словарь с id {dictionary['id']} уже существует")
            return False
        except sqlite3.Error as e:
            logger.error(f"Ошибка при вставке словаря: {e}")
            return False
    
    def insert_dictionaries(self, dictionaries: List[Dict]) -> bool:
        success_count = 0
        total_count = len(dictionaries)
        
        for dictionary in dictionaries:
            if self.insert_dictionary(dictionary):
                success_count += 1
        
        logger.info(f"Успешно добавлено {success_count} из {total_count} словарей")
        return success_count == total_count
    
    def get_dictionary_by_id(self, dict_id: int) -> Optional[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, own_password, com_password 
                    FROM dictionaries 
                    WHERE id = ?
                ''', (dict_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        'id': result[0],
                        'own_password': result[1],
                        'com_password': result[2]
                    }
                else:
                    logger.warning(f"Словарь с id {dict_id} не найден")
                    return None
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении словаря: {e}")
            return None
    
    def get_all_dictionaries(self) -> List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, own_password, com_password 
                    FROM dictionaries 
                    ORDER BY id
                ''')
                results = cursor.fetchall()
                
                dictionaries = []
                for result in results:
                    dictionaries.append({
                        'id': result[0],
                        'own_password': result[1],
                        'com_password': result[2]
                    })
                
                logger.info(f"Получено {len(dictionaries)} словарей")
                return dictionaries
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении всех словарей: {e}")
            return []
    
    def update_dictionary(self, dictionary: Dict) -> bool:
        required_keys = {'id', 'own_password', 'com_password'}
        if not all(key in dictionary for key in required_keys):
            logger.error(f"Словарь должен содержать ключи: {required_keys}")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE dictionaries 
                    SET own_password = ?, com_password = ?
                    WHERE id = ?
                ''', (dictionary['own_password'], dictionary['com_password'], dictionary['id']))
                
                if cursor.rowcount == 0:
                    logger.warning(f"Словарь с id {dictionary['id']} не найден для обновления")
                    return False
                
                conn.commit()
                logger.info(f"Словарь с id {dictionary['id']} успешно обновлен")
                return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка при обновлении словаря: {e}")
            return False
    
    def delete_dictionary(self, dict_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM dictionaries WHERE id = ?', (dict_id,))
                
                if cursor.rowcount == 0:
                    logger.warning(f"Словарь с id {dict_id} не найден для удаления")
                    return False
                
                conn.commit()
                logger.info(f"Словарь с id {dict_id} успешно удален")
                return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка при удалении словаря: {e}")
            return False
    
    def get_dictionaries_count(self) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM dictionaries')
                count = cursor.fetchone()[0]
                return count
        except sqlite3.Error as e:
            logger.error(f"Ошибка при подсчете словарей: {e}")
            return 0
    
    def clear_all_dictionaries(self) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM dictionaries')
                conn.commit()
                logger.info("Все словари удалены из базы данных")
                return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка при очистке таблицы: {e}")
            return False


def save_dictionary(db_path: str, dictionary: Dict) -> bool:
    manager = DictionaryManager(db_path)
    return manager.insert_dictionary(dictionary)

def save_dictionaries(db_path: str, dictionaries: List[Dict]) -> bool:
    manager = DictionaryManager(db_path)
    return manager.insert_dictionaries(dictionaries)

def load_dictionary(db_path: str, dict_id: int) -> Optional[Dict]:
    manager = DictionaryManager(db_path)
    return manager.get_dictionary_by_id(dict_id)

def load_all_dictionaries(db_path: str) -> List[Dict]:
    manager = DictionaryManager(db_path)
    return manager.get_all_dictionaries()



"""Experiments in course search algorithms."""
import time

import torch
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from sqrl import create_app
from sqrl.models import Course, Campus


CAMPUS_NAMES = {
    Campus.ST_GEORGE: 'St George',
    Campus.SCARBOROUGH: 'Scarborough',
    Campus.MISSISSAUGA: 'Mississauga'
}

app = create_app()
with app.app_context():
    COURSES = list(Course.objects.all())


def vectorise_courses(courses: list[Course], model: SentenceTransformer) -> np.ndarray:
    """Vectorise the given list of courses and output the vectors to a file."""
    documents = []
    for course in courses:
        br_str = f'Breath Requirements: {course.breadth_categories}'
        campus_str = CAMPUS_NAMES[course.campus]
        
        year_str = {
            0: 'zeroth',
            100: 'first',
            200: 'second',
            300: 'third',
            400: 'fourth'
        }[course.level]
        level_str = f'{course.level} level / {year_str} year'
        document = f'{course.code}: {course.title}\n{course.description}\n{br_str}\n{campus_str}\n{level_str}'
        documents.append(document)
    
    return model.encode(documents, show_progress_bar=True, convert_to_numpy=True)


def vector_search(query: str, model: SentenceTransformer, index: np.ndarray, k: int = 10) \
        -> tuple[np.ndarray, np.ndarray]:
    """Tranforms query to vector using a sentence-level transformer model and finds similar
    vectors using FAISS. Returns the ids of the top k results and their distances.    

    Args:
        query: The query string to search for.
        model: The pretrained SentenceTransformer model.
        index: The FAISS index.
        k: The number of results to return.
    """
    vector = model.encode([query])
    distances, indices = index.search(np.array(vector).astype(np.float32), k=k)
    return indices, distances


def search_course(query: str, model: SentenceTransformer, index: np.ndarray, k: int = 10) \
        -> list[Course]:
    """Search for a course using the given model and FAISS index.

    Args:
        query: The query string to search for.
        model: The pretrained SentenceTransformer model.
        index: The FAISS index.
        k: The number of results to return.
    """
    indices, _ = vector_search(query, model, course_index)
    return [COURSES[i] for i in indices[0]]
    

if __name__ == '__main__':
    # Load pre-trained model
    print('Loading model...')
    model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
    if torch.cuda.is_available():
        # Use cuda if available
        model = model.to(torch.device('cuda'))
    # Vectorise the courses
    print('Vectorising courses...')
    embeddings = vectorise_courses(COURSES, model).astype(np.float32)
    # Index embedding vectors
    course_index = faiss.IndexFlatL2(embeddings.shape[1])
    course_index = faiss.IndexIDMap(course_index)
    course_index.add_with_ids(embeddings, np.arange(len(COURSES)).astype(np.int64))

    # mat137_index = [course.id for course in courses].index('MAT137Y1-Y-20219')
    # D, I =  index.search(np.array([embeddings[mat137_index]]), k=10)
    # # Top 10 nearest courses to MAT137Y1-Y-20219
    # for i in I.flatten().tolist():
    #     print(courses[i].code, courses[i].title)

    # print(f'Performing query "{query}"...')
    # start_time = time.time()
    
    # print(f'Found {len(indices[0])} results in {time.time() - start_time} seconds.')
    # for index, (course_index, distance) in enumerate(zip(indices[0], distances[0])):
    #     course = courses[course_index]
    #     print(f'{index + 1}. {course.code}: {course.title} ({distance})')
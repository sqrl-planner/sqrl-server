"""Asymetrically course searching algorithm using Pre-trained MS MARCO models."""
import time

import torch
import numpy as np
from sentence_transformers import SentenceTransformer, util

from sqrl import create_app
from sqrl.models import Course, Campus


def get_courses() -> list[Course]:
    """Returns a list of courses."""
    print('Loading courses...')
    start_time = time.time()
    app = create_app()
    with app.app_context():
        courses = list(Course.objects.all())
        print(
            f'Loaded {len(courses)} courses in {time.time() - start_time} seconds.')
        return courses


def load_model(model_name: str = 'msmarco-distilbert-base-v4',
               ) -> SentenceTransformer:
    """Loads the pretrained model."""
    print(f'Loading model "{model_name}""...')
    start_time = time.time()
    model = SentenceTransformer(model_name)
    if torch.cuda.is_available():
        # Use cuda if available
        model = model.to(torch.device('cuda'))
        print('Using GPU')
    print(f'Loaded model in {time.time() - start_time} seconds.')
    return model


# def vectorise_courses(courses: list[Course], model: SentenceTransformer) \
#         -> tuple[int, np.ndarray]:
#     print('Vectorising courses...')
#     start_time = time.time()

#     documents = []
#     for course in courses:
#         br_str = f'Breath Requirements: {course.breadth_categories}'
#         year_str = {
#             0: 'zeroth',
#             100: 'first',
#             200: 'second',
#             300: 'third',
#             400: 'fourth'
#         }[course.level]
#         level_str = f'level {course.level}'
#         year_str = f'{year_str} year'
#         documents.extend([course.code, course.title, course.description, br_str, level_str, year_str])

#     n_tags = len(documents) // len(courses)
#     embeddings = model.encode(documents, show_progress_bar=True, convert_to_numpy=True)
#     print(f'Vectorised {len(documents)} courses in {time.time() - start_time} seconds.')
#     return n_tags, embeddings.reshape((len(courses), n_tags, -1))


def vectorise_courses(courses: list[Course],
                      model: SentenceTransformer) -> np.ndarray:
    CAMPUS_NAMES = {
        Campus.ST_GEORGE: 'St George',
        Campus.SCARBOROUGH: 'Scarborough',
        Campus.MISSISSAUGA: 'Mississauga',
    }

    print('Vectorising courses...')
    start_time = time.time()

    documents = []
    for course in courses:
        campus_str = CAMPUS_NAMES[course.campus]
        year_str = {0: 'zeroth', 100: 'first', 200: 'second', 300: 'third', 400: 'fourth', }[
            course.level
        ]
        documents.append(
            f'{course.code}, {course.title}, is a {year_str} year course (level '
            f'{course.level} course) at the {campus_str} campus. In {course.code} '
            f'students will learn: {course.description}.'.lower()
        )

    embeddings = model.encode(
        documents, show_progress_bar=True, convert_to_numpy=True)
    print(
        f'Vectorised {len(documents)} courses in {time.time() - start_time} seconds.')
    return embeddings


def search_courses(query: str, top_k: int = 10) -> list[Course]:
    """Returns the top k courses that match the query."""
    print('Searching courses...')
    start_time = time.time()

    query_vector = np.array(model.encode([query]))

    # query_vector_matrix = np.tile(query_vector, (n_tags, 1))
    # scores = []
    # tag_scores = []
    # for tag_embeddings in course_embeddings:
    #     x = np.linalg.norm(query_vector_matrix - tag_embeddings, axis=1)
    #     tag_scores.append(x)
    #     scores.append(np.mean(x, axis=0))
    # top_k_indices = np.argsort(scores)[:top_k]

    scores = util.pytorch_cos_sim(query_vector, course_embeddings)[0]
    top_results = torch.topk(scores, k=top_k)

    print('\n\n======================\n\n')
    print('Query:', query)
    print(f'Found {top_k} results in {time.time() - start_time} seconds:\n')

    for score, index in zip(top_results[0], top_results[1]):
        print(courses[index], f'(score: {score:.4f})')

    # for i in top_k_indices:
    #     score = scores[i]
    #     print(courses[i], f'(score: {score:.4f}, tags: {tag_scores[i]})')


courses = get_courses()
model = load_model()
course_embeddings = vectorise_courses(courses, model)

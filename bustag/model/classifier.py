'''
create classifier model and predict
'''
from sklearn.metrics import f1_score, recall_score, accuracy_score, precision_score, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from bustag.model.prepare import prepare_data, prepare_predict_data
from bustag.model.persist import load_model, dump_model
from bustag.spider.db import RATE_TYPE, ItemRate
from bustag.util import logger

model_path = './data/model/model.pkl'


def load():
    model_data = load_model(model_path)
    return model_data


def create_model():
    knn = KNeighborsClassifier(n_neighbors=11)
    return knn


def predict(X_test):
    model, _ = load()
    y_pred = model.predict(X_test)
    return y_pred


def train():
    model = create_model()
    X_train, X_test, y_train, y_test = prepare_data()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    confusion_mtx = confusion_matrix(y_test, y_pred)
    scores = evaluate(confusion_mtx, y_test, y_pred)
    models_data = (model, scores)
    dump_model(model_path, models_data)
    logger.info('new model trained')
    return models_data


def evaluate(confusion_mtx, y_test, y_pred):
    tn, fp, fn, tp = confusion_mtx.ravel()
    # accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    logger.info(f'tp: {tp}, fp: {fp}')
    logger.info(f'fn: {fn}, tn: {tn}')
    # logger.info(f'accuracy_score: {accuracy}')
    logger.info(f'precision_score: {precision}')
    logger.info(f'recall_score: {recall}')
    logger.info(f'f1_score: {f1}')
    model_scores = dict(precision=precision, recall=recall, f1=f1)
    model_scores = {key: float('{:.2f}'.format(value))
                    for key, value in model_scores.items()}
    return model_scores


def recommend():
    '''
    use trained model to recommend items
    '''
    ids, X = prepare_predict_data()
    count = 0
    total = len(ids)
    y_pred = predict(X)
    for id, y in zip(ids, y_pred):
        if y == 1:
            count += 1
            # print(id, y)
        rate_type = RATE_TYPE.SYSTEM_RATE
        rate_value = y
        item_id = id
        item_rate = ItemRate(rate_type=rate_type,
                             rate_value=rate_value, item_id=item_id)
        item_rate.save()
    return total, count


if __name__ == "__main__":
    total, count = recommend()
    print('total:', total)
    print('recommended:', count)
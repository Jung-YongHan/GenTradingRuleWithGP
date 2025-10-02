from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import datasets, metrics
from mealpy import FloatVar, StringVar, SMA, Problem


# Load the data set; In this example, the breast cancer dataset is loaded.
bc = datasets.load_breast_cancer()
X = bc.data
y = bc.target

# Create training and test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1, stratify=y)

sc = StandardScaler()
sc.fit(X_train)
X_train_std = sc.transform(X_train)
X_test_std = sc.transform(X_test)


class SvmOptimizedProblem(Problem):
    def __init__(self, bounds=None, minmax="max", data=None, **kwargs):
        self.data = data
        super().__init__(bounds, minmax, **kwargs)

    def obj_func(self, x):
        x_decoded = self.decode_solution(x)
        C_paras, kernel_paras = x_decoded["C_paras"], x_decoded["kernel_paras"]

        svc = SVC(C=C_paras, kernel=kernel_paras, random_state=1)
        # Fit the model
        svc.fit(X_train_std, y_train)
        # Make the predictions
        y_predict = svc.predict(X_test_std)
        # Measure the performance
        return metrics.accuracy_score(y_test, y_predict)


data = [X_train_std, X_test_std, y_train, y_test]
my_bounds = [
    FloatVar(lb=0.01, ub=1000., name="C_paras"),
    StringVar(valid_sets=('linear', 'poly', 'rbf', 'sigmoid'), name="kernel_paras")
]

problem = SvmOptimizedProblem(bounds=my_bounds, minmax="max", data=data)

model = SMA.OriginalSMA(epoch=50, pop_size=50)
model.solve(problem)

print(f"Best agent: {model.g_best}")
print(f"Best solution: {model.g_best.solution}")
print(f"Best accuracy: {model.g_best.target.fitness}")
print(f"Best parameters: {model.problem.decode_solution(model.g_best.solution)}")
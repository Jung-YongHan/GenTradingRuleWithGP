import unittest


class MyTestCase(unittest.TestCase) :
    ## https://realpython.com/primer-on-jinja-templating/
    def test_file(self) :
        from jinja2 import Environment, FileSystemLoader

        max_score = 100
        test_name = "Python Challenge"
        students = [
            {"name" : "Sandrine", "score" : 100},
            {"name" : "Gergeley", "score" : 87},
            {"name" : "Frieda", "score" : 92},
        ]

        environment = Environment(loader = FileSystemLoader("templates/"))
        template = environment.get_template("message.txt")

        for student in students :
            filename = f"message_{student['name'].lower()}.txt"
            content = template.render(
                student,
                max_score = max_score,  # 여러 Template에 공통적인 것을 관리하면 될듯함.
                test_name = test_name  # 여러 Template에 공통적인 것을 관리하면 될듯함.
            )
            with open(filename, mode = "w", encoding = "utf-8") as message :
                message.write(content)
                print(f"... wrote {filename}")

    def test_file_if(self) :
        from jinja2 import Environment, FileSystemLoader

        max_score = 100
        test_name = "Python Challenge"
        students = [
            {"name" : "Sandrine", "score" : 100},
            {"name" : "Gergeley", "score" : 87},
            {"name" : "Frieda", "score" : 92},
            {"name" : "Fritz", "score" : 40},
            {"name" : "Sirius", "score" : 75},
        ]

        environment = Environment(loader = FileSystemLoader("templates/"))
        template = environment.get_template("message2.txt")

        for student in students :
            filename = f"message_{student['name'].lower()}.txt"
            content = template.render(
                student,
                max_score = max_score,  # 여러 Template에 공통적인 것을 관리하면 될듯함.
                test_name = test_name  # 여러 Template에 공통적인 것을 관리하면 될듯함.
            )
            with open(filename, mode = "w", encoding = "utf-8") as message :
                message.write(content)
                print(f"... wrote {filename}")

    def test_file_html(self) :
        from jinja2 import Environment, FileSystemLoader

        environment = Environment(loader = FileSystemLoader("templates/"))
        results_filename = "students_results.html"
        results_template = environment.get_template("results.html")

        max_score = 100
        test_name = "Python Challenge"
        students = [
            {"name" : "Sandrine", "score" : 100},
            {"name" : "Gergeley", "score" : 87},
            {"name" : "Frieda", "score" : 92},
            {"name" : "Fritz", "score" : 40},
            {"name" : "Sirius", "score" : 75},
        ]

        context = {
            "students"  : students,
            "test_name" : test_name,
            "max_score" : max_score,
        }

        with open(results_filename, mode = "w", encoding = "utf-8") as results :
            results.write(results_template.render(context))
            print(f"... wrote {results_filename}")

if __name__ == '__main__' :
    unittest.main()

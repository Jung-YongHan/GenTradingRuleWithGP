import unittest
from jinja2 import Template

class MyTestCase(unittest.TestCase) :
    def test_variables(self) :
        template = """hostname {{ hostname }}
        no ip domain lookup
        ip domain name local.lab
        ip name-server {{ name_server_pri }}
        ip name-server {{ name_server_sec }}

        ntp server {{ ntp_server_pri }} prefer
        ntp server {{ ntp_server_sec }}"""

        data = {
            "hostname"        : "core-sw-waw-01",
            "name_server_pri" : "1.1.1.1",
            "name_server_sec" : "8.8.8.8",
            "ntp_server_pri"  : "0.pool.ntp.org",
            "ntp_server_sec"  : "1.pool.ntp.org",
        }

        j2_template = Template(template)

        print(j2_template.render(data))

    def test_variable2(self):

        template = "Device {{ name }} is a {{ type }} located in the {{ site }} datacenter."
        data = {
            "name" : "waw-rtr-core-01",
            "site" : "warsaw-01",
        }

        j2_template = Template(template)

        print(j2_template.render(data))

    def test_stricted_undefined(self):
        from jinja2 import Template, StrictUndefined

        template = "Device {{ name }} is a {{ type }} located in the {{ site }} datacenter."

        data = {
            "name" : "waw-rtr-core-01",
            "site" : "warsaw-01",
        }

        j2_template = Template(template, undefined = StrictUndefined) ## type이 정의되어 있지 않으면 오류 발생
        print(j2_template.render(data))

    def test_comment(self):
        from jinja2 import Template

        template = """hostname {{ hostname }}

        {# DNS configuration -#}
        no ip domain lookup
        ip domain name local.lab
        ip name-server {{ name_server_pri }}
        ip name-server {{ name_server_sec }}

        {# Time servers config, we should use pool.ntp.org -#}
        ntp server {{ ntp_server_pri }} prefer
        ntp server {{ ntp_server_sec }}
        ntp server {{ ntp_server_trd }}"""

        data = {
            "hostname"        : "core-sw-waw-01",
            "name_server_pri" : "1.1.1.1",
            "name_server_sec" : "8.8.8.8",
            "ntp_server_pri"  : "0.pool.ntp.org",
            "ntp_server_sec"  : "1.pool.ntp.org",
        }

        ## {# DNS configuration -#}
        ## 이렇게 하면 Comment로 됨
        j2_template = Template(template)
        print(j2_template.render(data))

if __name__ == '__main__' :
    unittest.main()

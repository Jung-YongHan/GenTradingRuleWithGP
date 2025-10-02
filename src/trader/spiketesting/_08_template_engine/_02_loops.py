import unittest


class MyTestCase(unittest.TestCase) :
    def test_loop(self) :
        from jinja2 import Template

        template = """# Configuring Prefix List
                    ip prefix-list PL_AS_65003_IN
                    {%- for line in PL_AS_65003_IN %}
                     {{ line -}}
                    {% endfor %}"""

        data = {
            "PL_AS_65003_IN" : ["permit 10.96.0.0/24","permit 10.97.11.0/24",
                                "permit 10.99.15.0/24","permit 10.100.5.0/25",
                                "permit 10.100.6.128/25"]
        }

        ## {# DNS configuration -#}
        ## 이렇게 하면 Comment로 됨
        j2_template = Template(template)
        print(j2_template.render(data))

    def test_dictionary(self) :
        from jinja2 import Template

        template = """
        {% for iname, idata in interfaces.items() -%}
            interface {{ iname }}
                description {{ idata.description }}
                ip address {{ idata.ipv4_address }}
        {% endfor %}"""

        data = {
            "interfaces" : {
                "Ethernet1": {
                    "description"  : "leaf01 - eth51",
                    "ipv4_address" : "10.50.0.0/31"
                },
                "Ethernet2" : {
                    "description"  : "leaf02 - eth51",
                    "ipv4_address" : "10.50.0.2/31"
                },
            }
        }

        ## {# DNS configuration -#}
        ## 이렇게 하면 Comment로 됨
        j2_template = Template(template)
        print(j2_template.render(data))

    def test_dictionary(self) :
        from jinja2 import Template

        template = """{% for intf in interfaces -%}
                           interface {{ intf }}
                             description {{ interfaces[intf].description }}
                             ip address {{ interfaces[intf].ipv4_address }}
                      {% endfor %}"""

        data = {
            "interfaces" : {
                "Ethernet1": {
                    "description"  : "leaf01 - eth51",
                    "ipv4_address" : "10.50.0.0/31"
                },
                "Ethernet2" : {
                    "description"  : "leaf02 - eth51",
                    "ipv4_address" : "10.50.0.2/31"
                },
            }
        }

        ## {# DNS configuration -#}
        ## 이렇게 하면 Comment로 됨
        j2_template = Template(template)
        print(j2_template.render(data))

    def test_dictionary2(self) :
        from jinja2 import Template

        template = """{% for intf in interfaces -%}
                           interface {{ intf }}
                             description {{ interfaces[intf].description }}
                             ip address {{ interfaces[intf].ipv4_address }}
                      {% endfor %}"""

        data = {
            "interfaces" : {
                "Ethernet1": {
                    "description"  : "leaf01 - eth51",
                    "ipv4_address" : "10.50.0.0/31"
                },
                "Ethernet2" : {
                    "description"  : "leaf02 - eth51",
                    "ipv4_address" : "10.50.0.2/31"
                },
            }
        }

        ## {# DNS configuration -#}
        ## 이렇게 하면 Comment로 됨
        j2_template = Template(template)
        print(j2_template.render(data))

    def test_loop2(self) :
        from jinja2 import Template

        template = """# Configuring Prefix List
{% for pl_name, pl_lines in prefix_lists.items() -%}
    ip prefix-list {{ pl_name }}    
    {%- for line in pl_lines %}
        {{ line -}}
    {%  endfor -%}
{% endfor %}"""

        data = {
            "prefix_lists": {
                        "PL_AS_65003_IN" : ["permit 10.96.0.0/24",
                                            "permit 10.97.11.0/24",
                                            "permit 10.99.15.0/24",
                                            "permit 10.100.5.0/25",
                                            "permit 10.100.6.128/25"]
                        }
        }
        j2_template = Template(template)
        print(j2_template.render(data))

if __name__ == '__main__' :
    unittest.main()

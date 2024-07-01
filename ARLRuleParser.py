import re
from pathlib import Path

class ARLRuleParser:

    @staticmethod
    def parse_arl_rule(rule_text):
        # Regular expressions for extracting rule components
        patterns = {
            "name": r"rule `(.+?)` \{",
            "priority": r"property priority = (\d+);",
            "effective_date": r"effectiveDate = new java\.util\.Date\(\"(.+?)\"\);",
            "expiration_date": r"expirationDate = new java\.util\.Date\(\"(.+?)\"\);",
            "status": r"status = \"(.+?)\";",
            "conditions": r"when \{(.*?)\}",
            "actions": r"then \{(.*?)\}"
        }

        rule = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, rule_text, re.DOTALL)
            if match:
                rule[key] = match.group(1).strip()
        
        return rule

    @staticmethod
    def convert_arl_to_drl(rule):
        salience = rule.get("priority", "")
        conditions = rule.get("conditions", "")
        actions = rule.get("actions", "")

        # Convert conditions
        conditions = conditions.replace(
            "com.bl.drools.demo.Customer() from $EngineData.this.customer;", 
            "customerObject: Customer()"
        )
        conditions = conditions.replace(
            "evaluate ( $EngineData.this.customer.totalSpending >= 100);", 
            "customerObject: Customer(totalSpending > 100)"
        )

        # Convert actions
        actions = actions.replace(
            "$EngineData.this.customer.discount = 5;", 
            "customerObject.setDiscount(5);"
        )

        drl_rule = f"""
dialect  "mvel"
rule "{rule.get('name', '')}"
    salience {salience}
when
    {conditions}
then
    {actions}
end
"""
        return drl_rule.strip()

    @staticmethod
    def write_drl_string_to_file(drl_rule_str, file_path):
        try:
            # Ensure the parent directories exist; create them if they don't
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the content to the file
            path.write_text(drl_rule_str, encoding='utf-8')
            
            # Print success message
            print("File written successfully.")
        except IOError as e:
            # Print the exception if an error occurs
            print(e)

if __name__ == "__main__":
    # Example ARL rule string
    arl_rule = (
        "rule `New customer and a big spender at birthday offer` {\n"
        "  property priority = 8;\n"
        "  effectiveDate = new java.util.Date(\"6/20/2024 0:00 +0200\");\n"
        "  expirationDate = new java.util.Date(\"6/23/2024 0:00 +0200\");\n"
        "  ilog.rules.business_name = \"rule one\";\n"
        "  ilog.rules.dt = \"\";\n"
        "  ilog.rules.package_name = \"\";\n"
        "  status = \"new\";\n"
        "  when {\n"
        "    com.bl.drools.demo.Customer() from $EngineData.this.customer;\n"
        "    evaluate ( $EngineData.this.customer.totalSpending >= 100);\n"
        "  }\n"
        "  then {\n"
        "    $EngineData.this.customer.discount = 5;\n"
        "  }\n"
        "}\n"
    )

    # The path to the file
    file_path = "C:\\Users\\boubouthiam.niang\\workspace\\bl\\rbms\\migration\\odmtodroolsbis\\src\\main\\resources\\rules\\rule.drl"

    # Parsing the ARL rule
    parsed_rule = ARLRuleParser.parse_arl_rule(arl_rule)

    # Converting to DRL format
    drl_rule = ARLRuleParser.convert_arl_to_drl(parsed_rule)

    # Write to DRL file
    ARLRuleParser.write_drl_string_to_file(drl_rule, file_path)

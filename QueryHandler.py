import re
"""
THIS IS WHERE THE INFIX -> POSTFIX
TRANSFORMATION HAPPENS
"""
class QueryHandler:
    def __init__(self, query):
        self.query = query
        self.infix = ""
        self.operators = "&|"
        self.postfix = ""
        self.keywordmap = []

    """
    Check which operation 
    has higher precedence
    """
    def getPrecedence(self, c):
        result = 0
        for char in self.operators:
            result += 1
        return result

    """
    Transform to postfix
    returns string of numbers and operators
    """
    def toPostfix(self):
        result = ""
        stack = list()
        result = "" 
        result_final = ""
        temp = ""
        count = 0
        for char in self.query:
            
            if self.isOperand(char): 
                result += char
            elif self.isOperator(char):
                while True:
                    if len(stack)> 0:
                        topChar = stack[-1]

                    if len(stack) == 0 or topChar == '(':
                        stack.append(char)
                        break
                    else:
                        precedence_char = self.getPrecedence(char)
                        precedence_top_char = self.getPrecedence(topChar)

                        if precedence_char > precedence_top_char:
                            stack.append(char)
                            break
                        else:    
                            result += stack.pop()

            elif char == '(':
                stack.append(char)
            elif char == ")":
                cpop = stack.pop()
                while cpop != '(':
                    result +=cpop
                    cpop = stack.pop()

        while len(stack) > 0:
            cpop = stack.pop()
            result+=cpop
        count_index = 0
        r_no_operators = re.sub(r'[^\w]', ' ', self.query)
        for keyword in r_no_operators.split(" "):
            if keyword in self.query and keyword!="": 
                result = result.replace(keyword, str(count_index))
                self.keywordmap.append(keyword)
                count_index+=1
        return result

    def getKeywordMapping(self):
        return self.keywordmap

    def isOperand(self, char):
        return ((char >= 'A' and char <= 'Z') or (char >= 'a' and char <="z"))  
    def isOperator(self, char):
        return char in self.operators


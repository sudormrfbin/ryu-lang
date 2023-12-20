(test-suite "literals"

  (test-case "true literal"
   :program
     "true"
   :untyped-ast
     (BoolLiteral :value True)
   :typed-ast
     (BoolLiteral Bool))

  (test-case "false literal"
   :program
     "false"
   :untyped-ast
     (BoolLiteral :value False)
   :typed-ast
     (BoolLiteral Bool))

  (test-case "positive int literal"
   :program
     "123"
   :untyped-ast
     (IntLiteral :value "123")
   :typed-ast
     (IntLiteral Int))

  (test-case "negative int literal"
   :program
     "-1"
   :untyped-ast
     (IntLiteral :value "-1")
   :typed-ast
     (IntLiteral Int)))

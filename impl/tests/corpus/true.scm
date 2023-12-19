(test-suite "literals"

  (test-case "true literal"
   :program
     "true"
   :untyped-ast
     (BoolLiteral :value True)
   :typed-ast
     (BoolLiteral Boolean))

  (test-case "false literal"
   :program
     "false"
   :untyped-ast
     (BoolLiteral :value False)
   :typed-ast
     (BoolLiteral Boolean))
)

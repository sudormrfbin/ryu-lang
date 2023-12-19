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
)

import unittest
import datetime

class Test_Suite_UC2():
    testmodules=[
        'test.test_case_TID1'
        'test.test_case_TID2'
    ]
    
    suite = unittest.TestSuite()
    for t in testmodules:
        print("...adding:",t)
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))
        
    print(datetime.datetime.now(), "test suite started")
    unittest.TextTestRunner().run(suite)
    
    
if __name__=='__main__':
    start = Test_Suite_UC2()
    start.allTests()
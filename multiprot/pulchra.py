"""
Author: Francisco Javier Guzman-Vega

Wrapper for PULCHRA - command line tool for all-atom reconstruction and
refinement of reduced protein models. PULCHRA can correct alpha carbon
positions, add backbone and side chain atoms, improve hydrogen bond patterns
and check proper protein chirality

http://www.pirx.com/pulchra/index.shtml

"""

import biskit as B
from biskit.exe.executor import Executor
import os, tempfile
import biskit.tools as T
from multiprot.errors import *

class Pulchra(Executor):
    """
    A Pulchra wrapper to add amino acid side chains to the linkers generated by Ranch

    Usage
    ====

    >>> call = Pulchra(f_in)

    >>> rebuild = call.run()

    The rebuilt model is created in the same directory as the input pdb

    """

    def __init__(self, model, **kw):
        
        """
        Create the variables that Pulchra needs to run

        :param f_in: path for the input pdb file to be rebuilt
        :type f_in: str

        :param kw:  additional key=value parameters are passed on to
                    'Executor.__init__'. For example:
                    ::
                        debug    -  0|1, keep all temporary files (default: 0)
                        verbose  -  0|1, print progress messages to log
                                        (log != STDOUT)
                        nice     -  int, nice level (default: 0)
                        log      -  biskit.LogFile, program log (None->STOUT)
                                        (default:None)
        """
        self.model = model

        tempdir = tempfile.mkdtemp('', self.__class__.__name__.lower() + '_',
            T.tempDir())
        
        pdb_path = os.path.join(tempdir, 'model.pdb')
        self.rb_path = pdb_path[:-3]+'rebuilt.pdb'

        self.model.writePdb(pdb_path)

        # Path for config file
        self.configpath = [os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'exeConfig/')]

        super().__init__('pulchra', tempdir=tempdir, configpath=self.configpath,
            args=pdb_path, **kw)

    def finish(self):
        """
        Overrides Executor method
        """

        rebuilt = B.PDBModel(self.rb_path)
        rebuilt.renumberResidues()

        self.result = rebuilt

    def cleanup(self):
        """
        Delete temporary files
        """
        if not self.debug:
            T.tryRemove(self.tempdir, tree=True)



#############
##  TESTING        
#############
import multiprot.testing as testing

class TestPulchra(testing.AutoTest):
    """
    Test class
    """

    TAGS = [testing.EXE]

    testpdb = None

    def setUp(self):
        self.testpdb =  self.testpdb or \
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                'testdata/2z6o.pdb')

    def test_rebuiltFile(self):
        """
        Test to confirm that .rebuilt.pdb file was created after running pulchra
        """
        pdb = B.PDBModel(self.testpdb)
        
        call = Pulchra(pdb)
        rebuilt = call.run()
        
        self.assertTrue(isinstance(rebuilt,B.PDBModel))


if __name__ == '__main__':

    testing.localTest(debug=False)

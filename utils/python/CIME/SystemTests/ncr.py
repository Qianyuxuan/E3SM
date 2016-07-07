"""
Implementation of the CIME NCR test.  This class inherits from SystemTestsCommon

Build two exectuables for this test, the first is a default build the
second halves the number of tasks and runs two instances for each component
Lay all of the components out concurrently
"""
import shutil
from CIME.XML.standard_module_setup import *
from CIME.case import Case
from CIME.case_setup import case_setup
import CIME.utils
from system_tests_common import SystemTestsCommon

class NCR(SystemTestsCommon):

    def __init__(self, case):
        """
        initialize a test object
        """
        SystemTestsCommon.__init__(self, case)

    def build(self):
        exeroot = self._case.get_value("EXEROOT")
        cime_model = CIME.utils.get_model()

        machpes1 = os.path.join("LockedFiles","env_mach_pes.NCR1.xml")
        if ( os.path.isfile(machpes1) ):
            shutil.copy(machpes1,"env_mach_pes.xml")

        # Build two exectuables for this test, the first is a default build, the
        # second halves the number of tasks and runs two instances for each component
        # Lay all of the components out concurrently
        for bld in range(1,3):
            logging.warn("Starting bld %s"%bld)
            machpes = os.path.join("LockedFiles","env_mach_pes.NCR%s.xml"%bld)
            ntasks_sum = 0
            for comp in ['ATM','OCN','WAV','GLC','ICE','ROF','LND']:
                self._case.set_value("NINST_%s"%comp,str(bld))
                ntasks      = self._case.get_value("NTASKS_%s"%comp)
                if(bld == 1):
                    self._case.set_value("ROOTPE_%s"%comp, 0)
                    if ( ntasks > 1 ):
                        self._case.set_value("NTASKS_%s"%comp, ntasks/2)
                else:
                    self._case.set_value("ROOTPE_%s"%comp, ntasks_sum)
                    ntasks_sum += ntasks*2
                    self._case.set_value("NTASKS_%s"%comp, ntasks*2)
            self._case.flush()

            case_setup(self._case, test_mode=True, reset=True)
            self.clean_build()
            SystemTestsCommon.build(self)
            shutil.move("%s/%s.exe"%(exeroot,cime_model),
                        "%s/%s.exe.NCR%s"%(exeroot,cime_model,bld))
            shutil.copy("env_build.xml",os.path.join("LockedFiles","env_build.NCR%s.xml"%bld))
            shutil.copy("env_mach_pes.xml", machpes)

        # Because mira/cetus interprets its run script differently than
        # other systems we need to copy the original env_mach_pes.xml back
        shutil.copy(machpes1,"env_mach_pes.xml")
        shutil.copy("env_mach_pes.xml",
                    os.path.join("LockedFiles","env_mach_pes.xml"))

    def run(self):
        os.chdir(self._caseroot)

        exeroot = self._case.get_value("EXEROOT")
        cime_model = CIME.utils.get_model()

        # Reset beginning test settings
        expect(os.path.exists("LockedFiles/env_mach_pes.NCR1.xml"),
               "ERROR: LockedFiles/env_mach_pes.NCR1.xml does not exist\n"
               "   this would been produced in the build - must run case.test_build")

        shutil.copy("LockedFiles/env_mach_pes.NCR1.xml", "env_mach_pes.xml")
        shutil.copy("env_mach_pes.xml", "LockedFiles/env_mach_pes.xml")
        shutil.copy("%s/%s.exe.NCR1" % (exeroot, cime_model),
                    "%s/%s.exe" % (exeroot, cime_model))
        shutil.copy("LockedFiles/env_build.NCR1.xml", "env_build.xml")
        shutil.copy("env_build.xml", "LockedFiles/env_build.xml")

        stop_n      = self._case.get_value("STOP_N")
        stop_option = self._case.get_value("STOP_OPTION")

        self._case.set_value("HIST_N", stop_n)
        self._case.set_value("HIST_OPTION", stop_option)
        self._case.set_value("CONTINUE_RUN", False)
        self._case.set_value("REST_OPTION", "none")
        self._case.flush()

        #======================================================================
        # do an initial run test with NINST 1
        #======================================================================
        logger.info("default: doing a %s %s with NINST1" % (stop_n, stop_option))
        success = SystemTestsCommon.run(self)

        #======================================================================
        # do an initial run test with NINST 2
        # want to run on same pe counts per instance and same cpl pe count
        #======================================================================

        if success:
            os.remove("%s/%s.exe" % (exeroot, cime_model))
            shutil.copy("%s/%s.exe.NCR2" % (exeroot, cime_model),
                        "%s/%s.exe" % (exeroot, cime_model))
            shutil.copy("LockedFiles/env_build.NCR2.xml", "env_build.xml")
            shutil.copy("env_build.xml", "LockedFiles/env_build.xml")

            logger.info("default: doing a %s %s with NINST2" % (stop_n, stop_option))
            success = SystemTestsCommon._run(self, "multiinst")

        # Compare
        if success:
            return self._component_compare_test("base", "multiinst")
        else:
            return False

    def report(self):
        SystemTestsCommon.report(self)

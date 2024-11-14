# Illustrates how fcidump file containing fragment hamiltonian
# can be generated using be2fcidump

import os
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

import numpy as np
import pytest
from pyscf.tools import fcidump

from molbe import BE, fragpart
from molbe.misc import be2fcidump, libint2pyscf


def prepare_system():
    # Read in molecular integrals expressed in libint basis ordering
    # numpy.loadtxt takes care of the input under the hood
    mol, mf = libint2pyscf(
        "data/octane.xyz", "data/hcore_libint_octane.dat", "STO-3G", hcore_skiprows=1
    )
    mf.kernel()

    # Construct fragments for BE
    fobj = fragpart(be_type="be2", mol=mol)
    oct_be = BE(mf, fobj)
    return oct_be

@pytest.mark.skipif(not os.getenv("QUEMB_DO_KNOWN_TO_FAIL_TESTS") == "true",
                    reason="This test is known to fail.")
def test_fcidump_writing():
    oct_be = prepare_system()
    tmp_dir = Path(mkdtemp())
    data_dir = Path("data/octane_FCIDUMPs/")

    # Write out fcidump file for each fragment
    be2fcidump(oct_be, str(tmp_dir / "octane"), "fragment_mo")

    for i in range(6):
        reference = fcidump.read(data_dir / f'octanef{i}')
        new = fcidump.read(tmp_dir / f'octanef{i}')

        if (abs(new["H1"] - reference["H1"]).max() > 1e-5):
            print(reference["H1"][abs(new["H1"] - reference["H1"]) > 1e-5])


        assert np.allclose(new["H1"], reference["H1"])
        assert np.allclose(new["H2"], reference["H2"])
    rmtree(tmp_dir)


if __name__ == "__main__":
    test_fcidump_writing()
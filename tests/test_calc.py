import pytest
from ase.build import bulk, molecule
from ase.optimize import BFGS

from xtb_ase.calculator import XTB, XTBProfile


def test_molecule_static(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    atoms = molecule("H2O")
    atoms.calc = XTB()
    atoms.get_potential_energy()
    results = atoms.calc.results
    attributes = results["attributes"]
    assert results["energy"] == pytest.approx(-137.9677709332199)
    assert attributes["charge"] == 0
    assert attributes["metadata"]["package"] == "xTB"
    assert attributes["metadata"]["methods"] == ["GFN2-xTB"]
    assert attributes["metadata"]["coord_type"] == "xyz"
    assert attributes["scfenergies"][-1] == results["energy"]
    assert "--tblite" not in attributes["metadata"]["keywords"]


def test_molecule_static_gfnff(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    atoms = molecule("H2O")
    atoms.calc = XTB(method="gfn-ff")
    atoms.get_potential_energy()
    results = atoms.calc.results
    attributes = results["attributes"]
    assert results["energy"] == pytest.approx(-8.91266686965633)
    assert attributes["charge"] == 0
    assert attributes["metadata"]["package"] == "xTB"
    assert attributes["metadata"]["methods"] == ["GFN-FF"]
    assert attributes["metadata"]["coord_type"] == "xyz"
    assert attributes["scfenergies"][-1] == results["energy"]
    assert "--gfnff" in attributes["metadata"]["keywords"]
    assert "--tblite" not in attributes["metadata"]["keywords"]


def test_molecule_static_profile(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    atoms = molecule("H2O")
    atoms.calc = XTB(profile=XTBProfile(argv=["xtb", "--tblite"]))
    atoms.get_potential_energy()
    results = atoms.calc.results
    attributes = results["attributes"]
    assert results["energy"] == pytest.approx(-137.9677709332199)
    assert attributes["metadata"]["package"] == "xTB"
    assert attributes["metadata"]["coord_type"] == "xyz"
    assert attributes["scfenergies"][-1] == results["energy"]
    assert "--gfn" in attributes["metadata"]["keywords"]
    assert "--tblite" in attributes["metadata"]["keywords"]


def test_bulk_static(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    atoms = molecule("CH3")
    atoms.calc = XTB(uhf=1)
    atoms.get_potential_energy()
    results = atoms.calc.results
    attributes = results["attributes"]
    assert results["energy"] == pytest.approx(-97.362345908)
    assert attributes["metadata"]["package"] == "xTB"
    assert attributes["metadata"]["coord_type"] == "xyz"
    assert attributes["scfenergies"][-1] == results["energy"]
    assert "--tblite" in attributes["metadata"]["keywords"]
    assert "--spinpol" in attributes["metadata"]["keywords"]


def test_molecule_spin_without_spinpol(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    atoms = molecule("CH3")
    atoms.calc = XTB(uhf=1, spinpol=False)
    atoms.get_potential_energy()
    results = atoms.calc.results
    attributes = results["attributes"]
    assert results["energy"] == pytest.approx(-96.946877312)
    assert attributes["metadata"]["package"] == "xTB"
    assert attributes["metadata"]["coord_type"] == "xyz"
    assert attributes["scfenergies"][-1] == results["energy"]
    assert "--tblite" not in attributes["metadata"]["keywords"]
    assert "--spinpol" not in attributes["metadata"]["keywords"]


def test_bulk_static_gfn1(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    atoms = bulk("Cu")
    atoms.calc = XTB(method="GFN1-xTB")
    atoms.get_potential_energy()
    results = atoms.calc.results
    attributes = results["attributes"]
    assert results["energy"] == pytest.approx(-130.73083354749846)
    assert attributes["metadata"]["package"] == "xTB"
    assert attributes["metadata"]["coord_type"] == "POSCAR"
    assert attributes["scfenergies"][-1] == results["energy"]
    assert "--gfn" in attributes["metadata"]["keywords"]
    assert "--tblite" in attributes["metadata"]["keywords"]


def test_bulk_static_detailed_input(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    atoms = bulk("Cu")
    atoms.calc = XTB(method="gfn1-xtb", scc={"temp": 500})
    atoms.get_potential_energy()
    results = atoms.calc.results
    attributes = results["attributes"]
    assert results["energy"] == pytest.approx(-130.73083354749846)
    assert attributes["metadata"]["package"] == "xTB"
    assert attributes["metadata"]["coord_type"] == "POSCAR"
    assert attributes["scfenergies"][-1] == results["energy"]
    assert "--gfn" in attributes["metadata"]["keywords"]
    assert "--tblite" in attributes["metadata"]["keywords"]


def test_bad(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError):
        XTB(method="bad")


def test_molecule_relax(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    atoms = molecule("H2O")
    atoms.calc = XTB()
    dyn = BFGS(atoms)
    dyn.run(fmax=0.01)
    results = atoms.calc.results
    attributes = results["attributes"]
    assert atoms != molecule("H2O")
    assert results["energy"] == pytest.approx(-137.976537)
    assert attributes["charge"] == 0
    assert attributes["metadata"]["package"] == "xTB"
    assert attributes["metadata"]["methods"] == ["GFN2-xTB"]
    assert attributes["metadata"]["coord_type"] == "xyz"
    assert attributes["scfenergies"][-1] == results["energy"]
    assert "--tblite" not in attributes["metadata"]["keywords"]


def test_molecule_internal_relax(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    atoms = molecule("H2O")
    profile = XTBProfile(["xtb", "--opt"])
    atoms.calc = XTB(profile=profile)

    atoms.get_potential_energy()

    results = atoms.calc.results
    attributes = results["attributes"]
    assert results["final_atoms"] != atoms
    assert results["energy"] == pytest.approx(-137.97654081)
    assert attributes["charge"] == 0
    assert attributes["metadata"]["package"] == "xTB"
    assert attributes["metadata"]["methods"] == ["GFN2-xTB"]
    assert attributes["metadata"]["coord_type"] == "xyz"
    assert attributes["scfenergies"][-1] == results["energy"]
    assert "--tblite" not in attributes["metadata"]["keywords"]

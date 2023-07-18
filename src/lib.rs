use pyo3::prelude::*;

mod arena;
mod consts;
mod macros;
mod py_helper;
mod rankings;
mod vec_ops;

// pub for bins
pub mod chi_type;
pub mod mjai;
pub mod state;

// pub for non-cfg(test) tests
pub mod agent;
pub mod tile;

// pub for benchmarks
pub mod algo;
pub mod hand;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn mjaisimulator(_py: Python, m: &PyModule) -> PyResult<()> {
    pyo3_log::init();

    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;

    let name = m.name()?;
    if cfg!(debug_assertions) {
        eprintln!("{name}: this is a debug build.");
        m.add("__profile__", "debug")?;
    } else {
        m.add("__profile__", "release")?;
    }
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    consts::register_module(_py, name, m)?;
    state::register_module(_py, name, m)?;
    arena::register_module(_py, name, m)?;

    Ok(())
}

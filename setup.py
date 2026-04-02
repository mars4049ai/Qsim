from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='qsim',
    version='1.0.0',
    license='MIT'
    description='Библиотека симуляции квантовых коммуникаций (BB84 QKD) и квантовой памяти',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'numpy>=1.24',
        'scipy>=1.10',
        'matplotlib>=3.7',
        'qutip>=5.0',
        'qiskit>=1.0',
        'qiskit-aer>=0.14',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Physics',
        'Intended Audience :: Science/Research',
    ],
)

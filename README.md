# Offical documentation

The official shapes documentation is at the [Crease Shapes ReadTheDocs](https://crease-shapes.readthedocs.io)

# Objects

## Setting Up the Project Environment

### Using Conda

1. **Create the Conda environment**:

   ```bash
   conda env create -f environment.yml

2. Activate the environment

```bash
conda activate my_project_env
```

## Creating structures

To create the structure of any filename, use:

```bash
python -m shapes_3d.objects.filename
```
The output should indicate where the `*.dump` file is located. 


## Visualizing *.dump files

1. Download [Ovito](https://www.ovito.org/#download) for your specific OS
2. Simply open the dump file within the software
3. It should show the plots of all objects, as specified in the dump file

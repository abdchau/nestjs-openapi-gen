# Introduction 
This is a generator for typescript nestjs backend code with DTOs, given OpenAPI specification, written in Python.

This generator does not attempt to be monolithic, instead focusing on providing a tool for the most common use case: writing a new endpoint in existing code and/or generating DTOs you don't want to type by hand.

 The generated code and DTOs contain annotations for Swagger. For more details, visit [@nestjs/swagger](https://www.npmjs.com/package/@nestjs/swagger). These may be made optional in the future.
 
# Getting Started
No dependencies are required.

The CLI assumes existence of a `source` folder in the root directory, which will contain the JSON representation of the OpenAPI specification in `endpoint.json`. Alternate paths can be specified at run time.

The output code will be contained in the `output` directory at root. Any existing files in the directory will be removed every time the CLI is run. 

When endpoints are generated, each endpoint's code and relevant DTOs will be generated in a separate folder. If two endpoints share a DTO, the DTO will be duplicated across folders.

# Run
Run `python main.py`.

You may choose to generate only DTOs, or endpoint stubs with DTOs.

# Contribute
Create your own fork and open a pull request. Contributions are very welcome!
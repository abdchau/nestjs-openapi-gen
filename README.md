# Introduction 
This is a generator for typescript nestjs backend code with DTOs, given an OpenAPI specification, written in Python.

This generator does not attempt to be monolithic, instead focusing on providing a tool for the most common use case: writing a new endpoint in existing code and/or generating DTOs you don't want to type by hand. 

It also possible to generate a full controller with all its endpoints. Controllers are specified by tags in the OpenAPI specification. This generator assumes, however, that the relevant module will be generated using NestJS's own generation tool (probably resource).

OpenAPI specifications can be generated using a visual tool. Many tools exist, both open source and proprietary. For the initiate, [Apicurio Studio](https://www.apicur.io/studio/) is a good start.

 The generated code and DTOs contain annotations for NestJS Swagger. For more details, visit [@nestjs/swagger](https://www.npmjs.com/package/@nestjs/swagger). These may be made optional in the future.
 
# Getting Started
No dependencies are required.

The CLI assumes existence of a `source` folder in the root directory, which will contain the JSON representation of the OpenAPI specification in `spec.json`. Alternate paths can be specified at run time. YAML representations are also supported, although it is not recommended due to significant performance effect. The yaml file must have a `.yaml` extension.

The output code will be contained in the `output` directory at root. Any existing files in the directory will be removed every time the CLI is run. 

When endpoints are generated, each endpoint's code and relevant DTOs will be generated in a separate folder. If two endpoints share a DTO, the DTO will be duplicated across folders.

When a controller is generated, all DTOs are consolidated into the `./dtos/` folder, as is the default behaviour of NestJS.

# Run
Run `python main.py`.

You may choose to generate only DTOs, endpoint stubs with DTOs, or full controllers with all endpoints and DTOs.

# Contribute
Create your own fork and open a pull request. Contributions are very welcome!
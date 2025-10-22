# infraspec.dev

![GitHub Action Lint](https://github.com/infraspecdev/infraspec.dev/actions/workflows/lint.yml/badge.svg?branch=main) [![Netlify Status](https://api.netlify.com/api/v1/badges/75646244-7bda-454b-98d1-5f8069237202/deploy-status?branch=main)](https://app.netlify.com/sites/infraspec/deploys)

## Getting Started

### Prerequisites

To run this website locally, you will need to have the following software installed on your computer:

- If you're using MacOS and [Homebrew](https://brew.sh/), you can install Hugo using the following command:

    ```bash
    brew install hugo
    ```

- If you're using a different operating system, you can find the installation instructions on the [Hugo website](https://gohugo.io/getting-started/installing/).
- The minimum version of Hugo required is available in [config.toml](config.toml) under `[module.hugoVersion]` key.

### Running the website locally

1. Clone the repository: `git clone https://github.com/infraspecdev/infraspec.dev.git`
2. Navigate to the directory: `cd infraspec.dev`
3. Run the website locally: `hugo server`
4. View the website in your browser at `http://localhost:1313`

### Adding yourselves to the team

1. Clone the repository (use this command:-  `git clone https://github.com/infraspecdev/infraspec.dev.git` )
2. Create `<yourfirstname>.md`(change to `your-first-second-name.md` in case of conflict) file in `content/team`.
3. Add your image in `static/images/team`. Ensure that you use a faceshot and image is not too large(< 2MB).
4. Push changes in a branch
5. See Netlify preview to check if everything is working as expected
6. Get PR merged.

## Contributions

Contributions are welcome! If you have any suggestions or find any bugs, please open an issue or create a pull request.

The pull requests support Netflify previews.

## License

This project is licensed under the [AGPL License](LICENSE).

## Acknowledgements

- [Hugo](https://gohugo.io/)
- [Netlify](https://www.netlify.com/)

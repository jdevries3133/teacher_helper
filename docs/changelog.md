# Changelog

## 2.0.1

- Update documentation and README

## v2.0.0

- incorporate codebase from [term 2
  grading](https://github.com/jdevries3133/term_2_grades) project into this
  library
  - `google` module (includes `google.classroom_wrapper`,
    `google.classroom_grader`, and `google.client`)
  - `docx` module includes `docx.RubricWriter`
- change `teacherhelper.Helper` to `teacherhelper.sis` (student information
  system). backwards compatibe APIs are preserved, but emit deprecation
  warnings and will be removed in v3
- Add CI/CD pipeline
- add tests for `helper` interface, and later for new `sis` module

## v1.0.1

- Add documentation in `./doc`
- Add very basic smoke tests
- Create ci/cd pipeline
- Create documentaton website

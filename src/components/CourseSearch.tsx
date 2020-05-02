import React, { CSSProperties, useState } from "react";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupText,
  Input,
  Container,
  FormGroup,
  Row,
  Col,
  Button,
  Form,
} from "reactstrap";

interface CourseSearchComponents {
  requestError: boolean;
  handleSubmit: (e: React.FormEvent<Element>, values: FormValues) => void;
  setValues: React.Dispatch<React.SetStateAction<FormValues>>;
  values: FormValues;
}

export interface FormValues {
  dep_name: string;
  crn: string;
  prof_name: string;
  class_name: string;
}

export const CourseSearch: React.FC<CourseSearchComponents> = ({
  requestError,
  handleSubmit,
  setValues,
  values,
}: CourseSearchComponents) => {
  const handleInputChange = (
    name: "crn" | "dep_name" | "prof_name" | "class_name",
    value: string
  ) => {
    switch (name) {
      case "crn":
        setValues({ ...values, crn: value });
        break;
      case "class_name":
        setValues({ ...values, class_name: value });
        break;
      case "prof_name":
        setValues({ ...values, prof_name: value });
        break;
      case "class_name":
        setValues({ ...values, class_name: value });
        break;
    }
  };

  const handleFormSubmit = (event: React.FormEvent) => {
    console.log(values);
    handleSubmit(event, values);
  };

  return (
    <>
      <Container fluid style={{ background: "#cbf1f5" }}>
        <Form
          onSubmit={(e) => handleFormSubmit(e)}
          data-testid={"class-search-form"}
          style={{ padding: "13px", width: "100%" }}
        >
          <Row>
            <Col xl={2}>
              <InputGroup>
                <InputGroupAddon addonType="prepend">
                  <InputGroupText>CRN</InputGroupText>
                </InputGroupAddon>
                <Input
                  name={"crn"}
                  value={values.crn}
                  onChange={(e) => handleInputChange("crn", e.target.value)}
                  placeholder="12345"
                  data-testid={"crn-input"}
                />
              </InputGroup>
            </Col>

            <Col xl={4}>
              <InputGroup>
                <InputGroupAddon addonType="prepend">
                  <InputGroupText>Class Name</InputGroupText>
                </InputGroupAddon>
                <Input
                  name={"class-name"}
                  value={values.class_name}
                  onChange={(e) =>
                    handleInputChange("class_name", e.target.value)
                  }
                  placeholder="Intro to Comp Science: Python"
                  data-testid={"class-input"}
                />
              </InputGroup>
            </Col>
            <Col xl={4}>
              <InputGroup>
                <InputGroupAddon addonType="prepend">
                  <InputGroupText>Professor Name</InputGroupText>
                </InputGroupAddon>
                <Input
                  name={"prof-name"}
                  value={values.prof_name}
                  onChange={(e) =>
                    handleInputChange("prof_name", e.target.value)
                  }
                  placeholder="Mike Rossetti"
                  data-testid={"prof-input"}
                />
              </InputGroup>
            </Col>
            <Col xl={2}>
              <Button type="submit" color="primary">
                {" "}
                Search{" "}
              </Button>
            </Col>
          </Row>
        </Form>
      </Container>
    </>
  );
};

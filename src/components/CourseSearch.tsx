import React, { CSSProperties } from "react";
import { InputGroup, InputGroupAddon, InputGroupText, Input, Container } from "reactstrap";

interface CourseSearchComponents {
  requestError: boolean;
  handleCRNSubmit: (e: React.FormEvent<Element>) => void;
  setInputCRN: React.Dispatch<React.SetStateAction<string>>;
  inputCRN: string;
}

export const CourseSearch: React.FC<CourseSearchComponents> = ({
  requestError,
  handleCRNSubmit,
  setInputCRN,
  inputCRN,
}: CourseSearchComponents) => {

  const errorStyle: CSSProperties = {
    borderColor: "red",
  };

  return (
    <>
    <Container>
      <form onSubmit={(e) => handleCRNSubmit(e)}>
        <InputGroup>
          <InputGroupAddon addonType="prepend">
            <InputGroupText>CRN</InputGroupText>
          </InputGroupAddon>
          <Input
            name={"crn"}
            value={inputCRN}
            onChange={(e) => setInputCRN(e.target.value)}
            placeholder="12345"
            style={requestError ? errorStyle : undefined}
          />
        </InputGroup>
      </form>
      </Container>
    </>
  );
};

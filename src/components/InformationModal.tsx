import React, { Dispatch, SetStateAction, useState } from "react";
import {
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Spinner,
} from "reactstrap";

interface InformationModalProps {
  modal: boolean;
  toggle: () => void;
  setModal: Dispatch<SetStateAction<boolean>>;
  setMessage: Dispatch<SetStateAction<string>>;
  loading: boolean;
  execute: () => void;
  message: string;
  title: string;
  buttonSettings: ButtonSettings;
}

interface ButtonSettings {
  type: string;
  text: string;
}

export const InformationModal: React.FC<InformationModalProps> = ({
  modal,
  toggle,
  setModal,
  loading,
  execute,
  message,
  title,
  setMessage,
  buttonSettings,
}: InformationModalProps) => {
  const close = () => setModal(false);
  const [disabled, setDisabled] = useState(false);
  const handleAction = () => {
    execute();
    setDisabled(true);
  };

  const handleClose = () => {
    setDisabled(false);
    setMessage("");
    close();
  };

  const getContent = () => {
    if (buttonSettings.type == "success") {
      let processed = message.split("!");
      return (
        <>
          {processed.shift()}
          <ul>
            {processed.map((line) => {
              return <li>{line}</li>;
            })}
          </ul>
        </>
      );
    } else {
      return message;
    }
  };

  return (
    <>
      <Modal isOpen={modal} toggle={handleClose}>
        <ModalHeader toggle={handleClose}>{title}</ModalHeader>
        <ModalBody>
          {loading ? <Spinner size={"lg"} /> : getContent()}
        </ModalBody>
        <ModalFooter>
          <Button
            disabled={disabled}
            color={buttonSettings.type}
            onClick={handleAction}
          >
            {buttonSettings.text}
          </Button>{" "}
          <Button color="secondary" onClick={handleClose}>
            Cancel
          </Button>
        </ModalFooter>
      </Modal>
    </>
  );
};

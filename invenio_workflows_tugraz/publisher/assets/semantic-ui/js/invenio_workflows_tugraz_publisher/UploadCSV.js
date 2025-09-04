// This file is part of Invenio.
//
// Copyright (C) 2025 Graz University of Technology.
//
// invenio-workflows-tugraz is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.

import axios from "axios";
import React, { PureComponent } from "react";
import { connect } from "react-redux";
import {
  Button,
  Modal,
  ModalActions,
  ModalContent,
  ModalHeader,
} from "semantic-ui-react";

import { ShowProgress } from "@js/invenio_catalogue_marc21/deposit/components/ShowProgress";

function modalLocalReducer(state, action) {
  switch (action.type) {
    case "close":
      return { ...state, open: false };
    case "open":
      return { ...state, open: true, size: action.size };
    case "started":
      return { ...state, open: true, polling: true };
    default:
      return state;
  }
}

class UploadCSVCmp extends PureComponent {
  constructor(props) {
    super(props);
    this.state = {
      open: false,
      size: undefined,
      polling: false,
    };
    this.inputRef = React.createRef();
  }

  dispatch = (action) => {
    this.setState((prevState) => modalLocalReducer(prevState, action));
  };

  handleOpen = () => {
    this.dispatch({ type: "open", size: "mini" });
  };

  handleClose = () => {
    this.dispatch({ type: "close" });
  };

  handleStart = async () => {
    const { record } = this.props;
    const recid = record.id;
    try {
      let apiConfig = {
        withCredentials: true,
        xsrfCookieName: "csrftoken",
        xsrfHeaderName: "X-CSRFToken",
        headers: { Accept: "application/json" },
      };
      let axiosWithConfig = axios.create(apiConfig);
      const url = `/api/catalogue/tasks/start/${recid}/import?type=csv`;
      await axiosWithConfig.get(url);
    } catch (error) {
      console.log("CreateNode error: ", error);
    }
    this.dispatch({ type: "started" });
  };

  render() {
    const { open, size, polling } = this.state;
    const { recid } = this.props;
    // - call to see if files have been uploaded (which will be processed)
    //   maybe also a green box if they have the correct format (Nice to have)
    // - button to start processing
    // - polling to get the success imports (Nice to have)
    // - after all are successfuly imported with close update the view
    return (
      <>
        <Button
          compact
          fluid
          onClick={this.handleOpen}
          icon="file"
          labelPosition="left"
          content="Upload CSV"
        />
        <Modal size={size} open={open} onClose={this.handleClose}>
          <ModalHeader>Upload CSV + zip file</ModalHeader>
          <ModalContent>
            <Button onClick={this.handleStart}>Start Process</Button>
          </ModalContent>
          {/* <ModalContent>{polling && <ShowProgress recid={recid} />}</ModalContent> */}
          <ModalActions>
            <Button negative onClick={this.handleClose}>
              Close
            </Button>
            <Button positive onClick={this.handleUpload}>
              Upload
            </Button>
          </ModalActions>
        </Modal>
      </>
    );
  }
}

function save(data) {
  // maybe not necessary that complicated but it does work like that
  // name should be different, because it does not save the record
  // it does only updating the record
  return async (dispatch) => {
    dispatch({
      type: "DRAFT_SAVE_SUCCEEDED",
      payload: { data: data },
    });
  };
}

const mapStateToProps = null;

const mapDispatchToProps = (dispatch) => ({
  saveAction: (values) => dispatch(save(values)),
});

export const UploadCSV = connect(
  mapStateToProps,
  mapDispatchToProps,
)(UploadCSVCmp);

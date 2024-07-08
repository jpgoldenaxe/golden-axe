import { useState, useEffect } from 'react';
import axios from 'axios';

import { CdsButton } from '@cds/react/button';
import { CdsModal, CdsModalHeader, CdsModalActions, CdsModalContent } from '@cds/react/modal';
import { CdsInput } from '@cds/react/input';
import { CdsRadio, CdsRadioGroup } from '@cds/react/radio';
import { CdsControlMessage, CdsFormGroup } from '@cds/react/forms';
import { CdsPassword } from '@cds/react/password';

// ConfigAPIパラメータの型
interface BkTargetType {
  _id: string;
  description: string;
  host: string;
  name: string;
  password: string;
  product_type: string;
  user: string;
}

// ArtifactAPIパラメータの型
interface BkJobType {
  _id: string;
  config_id: string;
  name: string;
  product_type: string,
  product_version: string;
  size: string;
  status: string;
  timestamp: string;
}

// ConfigAPI
const ConfigAPI = () => {
  const server = process.env.REACT_APP_APISERVER
    || '/api/v1/configs/';
  const [bkTarget, setBkTarget] = useState<Array<BkTargetType>>([]);

  const getBkTarget = async () => {
    const res = await axios.get(server);
    setBkTarget(res.data);
  };
  useEffect(() => { getBkTarget();}, []);

  const delBkTarget = async (id: string) => {
    try {
      const res = await axios.delete(server + id);
      if (res) getBkTarget();
    } catch (error) { console.error('Axios DELETE error:', error); }
  };

  const addBkTarget = async (data: {}) => {
    try {
      const res = await axios.post(server, data);
      if (res) getBkTarget();
    } catch (error) { console.error('Axios POST error:', error); }
  };

  return { bkTarget, delBkTarget, addBkTarget };
};

// ArtifactAPI
const ArtifactAPI = () => {
  const server = process.env.REACT_APP_APISERVER
    || '/api/v1/artifacts/';
  const [bkJob, setBkJob] = useState<Array<BkJobType>>([]);

  const getBkJob = async () => {
    const res = await axios.get(server);
    setBkJob(res.data);
  };
  useEffect(() => { getBkJob(); }, []);

  const delBkJob = async (id: string) => {
    try {
      const res = await axios.delete(server + id);
      if (res) getBkJob();
    } catch (error) { console.error('Axios DELETE error:', error); }
  };

  const addBkJob = async (data: {}) => {
    try {
      const param = { "config_id": data };
      const res = await axios.post(server, param);
      if (res) getBkJob();
    } catch (error) { console.error('Axios POST error:', error); }
  };

  return { bkJob, delBkJob, addBkJob };
};

// Backup対象の登録フォーム 
const BackupDataForm = ({ hide, setHide, add }: {
  hide: boolean; setHide: (value: boolean) => void; add: (data: {}) => void;
}) => {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const data: { [key: string]: string } = {};
    e.currentTarget.querySelectorAll('input').forEach(elm => {
      (elm.type !== 'radio') ? data[elm.name] = elm.value
        : (elm.checked) && (data["product_type"] = elm.value);
    });
    add(data);
  };

  const radioOptions = ['vcenter', 'nsxmgr'];
  return (
    <CdsModal hidden={hide} onCloseChange={() => setHide(true)}>
      <form onSubmit={handleSubmit}>
        <CdsModalHeader>
          <h3 cds-text="section" id="title">Backup Target Registration</h3>
        </CdsModalHeader>
        <br /><br />
        <CdsModalContent cds-layout="horizontal gap:lg">
          <CdsFormGroup layout="horizontal">
            <CdsRadioGroup>
              <label>Product Type</label>
              {radioOptions.map((option) => (
                <CdsRadio key={option}>
                  <label>{option}</label><input type="radio" value={option} />
                </CdsRadio>
              ))}
            </CdsRadioGroup>
            <CdsInput>
              <label>Appliance Name</label>
              <input name="name" placeholder="e.g. vc01.example.com" />
              <CdsControlMessage>Input your target name</CdsControlMessage>
            </CdsInput>
            <CdsInput>
              <label>Target Host</label>
              <input name="host" placeholder="e.g. 192.168.0.1:8000" />
              <CdsControlMessage>IP address or Domain name</CdsControlMessage>
            </CdsInput>
            <CdsInput>
              <label>Username</label>
              <input name="user" placeholder="e.g. administrator@vsphere.local" />
            </CdsInput>
            <CdsPassword>
              <label>Password</label>
              <input name="password" type="password" autoComplete="on" />
            </CdsPassword>
            <CdsInput>
              <label>Description</label>
              <input name="description" />
              <CdsControlMessage>Feel free to use it</CdsControlMessage>
            </CdsInput>
          </CdsFormGroup>
        </CdsModalContent>
        <br /><br /><br />
        <CdsModalActions>
          <CdsButton type="button" onClick={() => setHide(true)}>
            Cancel</CdsButton>
          <CdsButton type="submit" onClick={() => setHide(true)}>OK</CdsButton>
        </CdsModalActions>
      </form>
    </CdsModal>
  );
};

// Backup一覧テーブル
const BackupDataList = ({ data, del, select }: {
  data: BkTargetType[];
  del: (id: string) => void;
  select: (item: BkTargetType) => void;
}) => (
  <div className="backup-list">
    <table className="table">
      <caption>Backup List</caption>
      <thead key="backup-list">
        <tr>
          <th></th>
          <th>No.</th>
          <th></th>
          <th>Target ID</th>
          <th>Target Name</th>
          <th>Product Type</th>
          <th>Target Host</th>
          <th>Username</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>
        {data.map((item, i) => {
          return (
            <tr key={i}>
              <td>
                <input type="radio" name="backup-target" id={item._id}
                  onChange={() => select(item)} />
              </td>
              <td>{i + 1}</td>
              <td>
                <CdsButton key={item._id} size="sm"
                  onClick={() => del(item._id)}>Delete</CdsButton>
              </td>
              <td className="resource">{item._id}</td>
              <td className="resource">{item.name}</td>
              <td className="resource">{item.product_type}</td>
              <td className="resource">{item.host}</td>
              <td className="resource">{item.user}</td>
              <td className="resource">{item.description}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  </div>
);

// Job一覧テーブル
const BackupJobList = (
  { data, del }: { data: BkJobType[]; del: (id: string) => void }) =>
(
  <div className="backup-list">
    <table className="table">
      <caption>Backup List</caption>
      <thead key="backup-list">
        <tr>
          <th>No.</th>
          <th></th>
          <th>Product Type</th>
          <th>Product Ver.</th>
          <th>Appliance Name</th>
          <th>Timestamp</th>
          <th>Status</th>
          <th>Size</th>
        </tr>
      </thead>
      <tbody>
        {data.map((item, i) => {
          return (
            <tr key={i}>
              <td>{i + 1}</td>
              <td>
                <CdsButton key={item._id} size="sm"
                  onClick={() => del(item._id)}>Delete</CdsButton>
              </td>
              <td className="resource">{item.product_type}</td>
              <td className="resource">{item.product_version}</td>
              <td className="resource">{item.name}</td>
              <td className="resource">{item.timestamp}</td>
              <td className="resource">{item.status}</td>
              <td className="resource">{item.size}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  </div>
);

// メイン画面
const Backup = () => {
  const [hideForm, setHideForm] = useState(true);
  const [target, setTarget] = useState<BkTargetType | null>(null);
  const { bkTarget, delBkTarget, addBkTarget } = ConfigAPI();
  const { bkJob, delBkJob, addBkJob } = ArtifactAPI();

  return (
    <div className="content-container">
      <div className="content-area">
        <h1 cds-text="heading">Backup Targets</h1><br />
        <CdsButton status="success" onClick={() => setHideForm(false)}>
          Add a backup target</CdsButton>
        <BackupDataList data={bkTarget} del={delBkTarget} select={setTarget} />
        <BackupDataForm
          hide={hideForm} setHide={setHideForm} add={addBkTarget} />
        <br /><br /><hr /><br />
        <h1 cds-text="heading">Backup Jobs</h1>
        <h3>Target: {target && `${target.name} (${target._id})`}</h3>
        <br />
        <CdsButton status="success" onClick={
          () => target ? addBkJob(target._id) : alert('Target is not selected')
        }>Add a backup job</CdsButton>
        <BackupJobList data={bkJob} del={delBkJob} />
      </div>
    </div>
  );
}

export default Backup;

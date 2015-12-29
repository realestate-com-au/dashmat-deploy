import React, {Component, PropTypes} from 'react';
import styles from '/modules/custom.scaling/Scaling.css'
import WidgetBox from '/modules/python_dashing.core_modules.components/WidgetBox.jsx';
import {Table} from 'react-bootstrap';

export class InstanceCountModule extends WidgetBox {
  render_inner() {
    return (
      <div>
        <div style={{padding: "5px"}}>
          <h3>{this.props.title}</h3>
          {this.state.data.instance_counts.map((v, index) =>
            <p key={index}>
              {v[0]}: {v[1].alive} alive, {v[1].dead} dead
            </p>
          )}
        </div>
      </div>
    )
  }
}

InstanceCountModule.propTypes = {
  ...WidgetBox.propTypes,

  data: PropTypes.shape({
    instance_counts: PropTypes.array,
  }),
  title: PropTypes.string,
};

export class ScalingModule extends WidgetBox {
  render_td(options, key) {
    var inner = ""
    if (options != null) {
      inner = options.desired + " | " + options.alive + " | " + options.dead
    }
    var className = "active"
    if (options != null) {
      className = options.alive == options.desired && options.desired > 0 ? "success" : styles.yellow
      className = options["alive"] == 0 && options.desired > 0 ? styles.red : className
    }

    return (
      <td key={key} className={className}>{inner}</td>
    )
  }

  render_inner() {
    var data = this.state.data.applications.map((value, index) =>
      this.state.data.by_account.reduce((nxt, v) => Object.assign(nxt, {[v[0]]: value[1][v[0]]}), {application: value[0]})
    )

    var account_names = this.state.data.by_account.map(v => v[0]);
    var headers = [
      <th key={0}>Application</th>,
      ...account_names.map((name, index) => <th key={index+1}>{name}</th>)
    ]

    return (
      <div>
        <Table>
          <thead>
            <tr>
              {headers}
            </tr>
          </thead>
          <tbody>
            {data.map((v, index) =>
              <tr key={index}>
                <td className="info">{v.application}</td>
                {account_names.map((name, index) => this.render_td(v[name], index))}
              </tr>
            )}
          </tbody>
        </Table>
      </div>
    )
  }
}

ScalingModule.propTypes = {
  ...WidgetBox.propTypes,

  data: PropTypes.shape({
    by_account: PropTypes.object,
    applications: PropTypes.array,
  }),
  title: PropTypes.string,
};

